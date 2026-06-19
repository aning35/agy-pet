import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class AntigravityState:
    IDLE = 0x01
    THINKING = 0x02
    WAITING_CONFIRM = 0x03
    ERROR = 0x04
    
    @staticmethod
    def to_string(state):
        return {
            0x01: "IDLE",
            0x02: "THINKING",
            0x03: "WAITING_CONFIRM",
            0x04: "ERROR"
        }.get(state, "UNKNOWN")

class LogHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_pos = 0
        self.current_file = None

    def set_file(self, file_path):
        try:
            self.current_file = file_path
            with open(self.current_file, 'r', encoding='utf-8') as f:
                f.seek(0, 2) # Go to end of file
                self.last_pos = f.tell()
            print(f"[*] Started monitoring log file: {self.current_file}")
        except Exception as e:
            print(f"[-] Error setting file for monitoring: {e}")

    def on_modified(self, event):
        # In Windows, paths might have different slashes, so normalize for comparison
        if os.path.normpath(event.src_path) == os.path.normpath(self.current_file):
            self.read_new_lines()

    def read_new_lines(self):
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                f.seek(self.last_pos)
                new_data = f.read()
                self.last_pos = f.tell()
                
                if new_data:
                    lines = new_data.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            self.parse_line(line)
        except Exception as e:
            print(f"[-] Error reading log file: {e}")

    def parse_line(self, line):
        try:
            # Find the first '{' to ignore any prefixes like "1: "
            start_idx = line.find('{')
            if start_idx == -1: return
            
            data = json.loads(line[start_idx:])
            
            source = data.get("source", "")
            msg_type = data.get("type", "")
            status = data.get("status", "")
            content = str(data.get("content", ""))
            
            # 1. Global Error Checks
            if status == "ERROR" or msg_type == "ERROR" or msg_type == "SYSTEM_ERROR":
                self.callback(AntigravityState.ERROR, "System Error")
                return
                
            if "error: there was a problem" in content.lower() or "retries remaining" in content.lower() or "网络中断" in content or "重试" in content or "agent terminated due to error" in content.lower() or "http 400 bad request" in content.lower() or "invalid_request_error" in content.lower() or "\"type\":\"error\"" in content.lower():
                if source == "SYSTEM" or source == "USER_EXPLICIT":
                    self.callback(AntigravityState.ERROR, "Fatal Agent Error")
                    return
            
            if source == "USER_EXPLICIT" and msg_type == "USER_INPUT":
                self.callback(AntigravityState.THINKING, "Received user input")
                
            elif source == "MODEL" and msg_type == "PLANNER_RESPONSE":
                tool_calls = data.get("tool_calls", [])
                if tool_calls:
                    self.callback(AntigravityState.THINKING, f"Calling {len(tool_calls)} tools")
                    # Check for waiting confirmation patterns
                    for tc in tool_calls:
                        args = tc.get("args", {})
                        if tc.get("name") == "write_to_file" and "implementation_plan.md" in str(args.get("TargetFile", "")):
                            if "RequestFeedback\":true" in str(args.get("ArtifactMetadata", "")) or "RequestFeedback\": true" in str(args.get("ArtifactMetadata", "")):
                                self.callback(AntigravityState.WAITING_CONFIRM, "Waiting for plan review")
                        elif tc.get("name") == "run_command" and str(args.get("SafeToAutoRun", "")).lower() == "false":
                            self.callback(AntigravityState.WAITING_CONFIRM, "Waiting for command confirmation")
                elif content.strip():
                    self.callback(AntigravityState.IDLE, "Model response complete")
                else:
                    self.callback(AntigravityState.THINKING, "Intermediate model step")
            elif source == "SYSTEM":
                if "error" in content.lower():
                     self.callback(AntigravityState.ERROR, "System error detected")
                elif "the user has automatically approved" in content.lower():
                     self.callback(AntigravityState.THINKING, "Auto-approved")
        except Exception as e:
            print(f"[-] Error parsing log line: {e}")

def get_latest_conversation_log(brain_dir):
    try:
        if not brain_dir or not os.path.exists(brain_dir):
            print(f"[-] Brain directory not found: {brain_dir}")
            return None
            
        dirs = []
        try:
            for d in os.listdir(brain_dir):
                full_path = os.path.join(brain_dir, d)
                if os.path.isdir(full_path):
                    dirs.append(full_path)
        except Exception as e:
            print(f"[-] Error listing brain directory: {e}")
            return None
            
        valid_logs = []
        for d in dirs:
            try:
                log_dir = os.path.join(d, ".system_generated", "logs")
                log_file_jsonl = os.path.join(log_dir, "transcript.jsonl")
                log_file_txt = os.path.join(log_dir, "overview.txt")
                
                if os.path.exists(log_file_jsonl):
                    valid_logs.append(log_file_jsonl)
                if os.path.exists(log_file_txt):
                    valid_logs.append(log_file_txt)
            except Exception:
                pass # Skip directory if it has access issues or gets deleted mid-process
                
        if not valid_logs: 
            print("[-] No conversation log files found.")
            return None
            
        # Safely compute max by catching potential FileNotFoundError if a file gets deleted during check
        try:
            existing_logs = [log for log in valid_logs if os.path.exists(log)]
            if not existing_logs:
                return None
            return max(existing_logs, key=os.path.getmtime)
        except Exception as e:
            print(f"[-] Error sorting log files by mtime: {e}")
            existing_logs = [log for log in valid_logs if os.path.exists(log)]
            if existing_logs:
                return existing_logs[0]
            return None
    except Exception as e:
        print(f"[-] Error getting latest conversation log: {e}")
        return None

def get_today_statistics(brain_dir):
    stats = {
        "user_requests": 0,
        "model_steps": 0,
        "tool_calls": 0,
        "errors": 0,
        "user_chars": 0,
        "ai_chars": 0
    }
    
    try:
        if not brain_dir or not os.path.exists(brain_dir):
            return stats
            
        import datetime
        today = datetime.date.today()
        
        for d in os.listdir(brain_dir):
            full_path = os.path.join(brain_dir, d)
            if not os.path.isdir(full_path):
                continue
                
            log_file = os.path.join(full_path, ".system_generated", "logs", "transcript.jsonl")
            if not os.path.exists(log_file):
                continue
                
            # Check if the file was modified today
            mtime = os.path.getmtime(log_file)
            file_date = datetime.date.fromtimestamp(mtime)
            
            if file_date != today:
                continue
                
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        source = data.get("source", "")
                        msg_type = data.get("type", "")
                        status = data.get("status", "")
                        tool_calls = data.get("tool_calls", [])
                        
                        if source == "USER_EXPLICIT" and msg_type == "USER_INPUT":
                            stats["user_requests"] += 1
                            stats["user_chars"] += len(str(data.get("content", "")))
                        elif source == "MODEL" and msg_type == "PLANNER_RESPONSE":
                            stats["model_steps"] += 1
                            stats["tool_calls"] += len(tool_calls)
                            stats["ai_chars"] += len(str(data.get("content", "")))
                            stats["ai_chars"] += len(str(data.get("thinking", "")))
                            
                        if status == "ERROR" or msg_type == "ERROR" or msg_type == "SYSTEM_ERROR":
                            stats["errors"] += 1
                    except Exception:
                        pass
                        
        return stats
    except Exception as e:
        print(f"[-] Error parsing statistics: {e}")
        return stats


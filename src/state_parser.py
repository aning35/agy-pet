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
        self.current_file = file_path
        with open(self.current_file, 'r', encoding='utf-8') as f:
            f.seek(0, 2) # Go to end of file
            self.last_pos = f.tell()
        print(f"[*] Started monitoring log file: {self.current_file}")

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
            content = data.get("content", "")
            
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
        except json.JSONDecodeError:
            pass

def get_latest_conversation_log(brain_dir):
    if not brain_dir or not os.path.exists(brain_dir):
        print(f"[-] Brain directory not found: {brain_dir}")
        return None
        
    dirs = [os.path.join(brain_dir, d) for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d))]
    valid_logs = []
    for d in dirs:
        log_file = os.path.join(d, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(log_file):
            valid_logs.append(log_file)
            
    if not valid_logs: 
        print("[-] No conversation log files found.")
        return None
        
    return max(valid_logs, key=os.path.getmtime)

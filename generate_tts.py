import asyncio
import edge_tts
import os

PROFILES = {
    "zhuren": {
        "voice": "zh-CN-XiaoxiaoNeural",
        "texts": {
            "idle.mp3": "主人，当前任务已执行完毕，等待您的新指令。",
            "thinking.mp3": "主人，我正在飞速运转，处理您安排的任务中。",
            "waiting.mp3": "主人，有关键操作被拦截，需要您进行手动确认。",
            "error.mp3": "主人，运行过程中遇到了异常，请您查看报错信息。"
        }
    },
    "laoban": {
        "voice": "zh-CN-YunxiNeural",
        "texts": {
            "idle.mp3": "老板，工作搞定了，随时准备接下一个活儿！",
            "thinking.mp3": "老板，正在加班加点为您跑代码呢！",
            "waiting.mp3": "老板，这份执行计划需要您的签字确认！",
            "error.mp3": "老板，程序抛出异常了，看来有点麻烦！"
        }
    },
    "gege": {
        "voice": "zh-CN-XiaoyiNeural",
        "texts": {
            "idle.mp3": "哥哥，刚才的任务已经完成啦，我在乖乖等你哦！",
            "thinking.mp3": "哥哥，我正在很认真地思考和运行呢，马上就好！",
            "waiting.mp3": "哥哥，这里有一个操作需要你来帮我确认一下哦！",
            "error.mp3": "哥哥，呜呜，好像代码运行出错了，快来帮帮我！"
        }
    },
    "baobao": {
        "voice": "zh-CN-YunjianNeural",
        "texts": {
            "idle.mp3": "宝宝，我把任务搞定了，随时可以叫我哦！",
            "thinking.mp3": "宝宝，我正在努力动脑筋处理代码呢！",
            "waiting.mp3": "宝宝，这里有个操作需要你同意才能继续哦！",
            "error.mp3": "宝宝，哎呀，系统报了个错，有点心塞！"
        }
    }
}

async def generate():
    base_dir = r"d:\CodeWorkspace\agy-pet\assets\sounds"
    for profile, data in PROFILES.items():
        profile_dir = os.path.join(base_dir, profile)
        os.makedirs(profile_dir, exist_ok=True)
        
        voice = data["voice"]
        for filename, text in data["texts"].items():
            out_path = os.path.join(profile_dir, filename)
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(out_path)
            print(f"Generated {out_path} with text: {text}")

if __name__ == "__main__":
    asyncio.run(generate())

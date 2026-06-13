import asyncio
import edge_tts
import os

PROFILES = {
    "zhuren": {
        "voice": "zh-CN-XiaoxiaoNeural",
        "texts": {
            "idle.mp3": "主人，当前任务已执行完毕，等待您的新指令。",
            "thinking.mp3": "主人，我正在飞速运转，处理您安排的任务中。",
            "thinking_long.mp3": "主人，这个问题有点复杂，我还在努力思考中，请稍等哦。",
            "waiting.mp3": "主人，有关键操作被拦截，需要您进行手动确认。",
            "error.mp3": "主人，运行过程中遇到了异常，请您查看报错信息。"
        }
    },
    "laoban": {
        "voice": "zh-CN-YunxiNeural",
        "texts": {
            "idle.mp3": "老板，工作搞定了，随时准备接下一个活儿！",
            "thinking.mp3": "老板，正在加班加点为您跑代码呢！",
            "thinking_long.mp3": "老板，这任务有点难啃，我还在持续处理中，请稍候！",
            "waiting.mp3": "老板，这份执行计划需要您的签字确认！",
            "error.mp3": "老板，程序抛出异常了，看来有点麻烦！"
        }
    },
    "gege": {
        "voice": "zh-CN-XiaoyiNeural",
        "texts": {
            "idle.mp3": "哥哥，刚才的任务已经完成啦，我在乖乖等你哦！",
            "thinking.mp3": "哥哥，我正在很认真地思考和运行呢，马上就好！",
            "thinking_long.mp3": "哥哥，这个问题有点费脑筋，我还在这里乖乖运算哦，等我一下下！",
            "waiting.mp3": "哥哥，这里有一个操作需要你来帮我确认一下哦！",
            "error.mp3": "哥哥，呜呜，好像代码运行出错了，快来帮帮我！"
        }
    },
    "baobao": {
        "voice": "zh-CN-YunjianNeural",
        "texts": {
            "idle.mp3": "宝宝，我把任务搞定了，随时可以叫我哦！",
            "thinking.mp3": "宝宝，我正在努力动脑筋处理代码呢！",
            "thinking_long.mp3": "宝宝，这代码有点复杂，我还在努力思考中哦，稍等一下！",
            "waiting.mp3": "宝宝，这里有个操作需要你同意才能继续哦！",
            "error.mp3": "宝宝，哎呀，系统报了个错，有点心塞！"
        }
    },
    "baba": {
        "voice": "zh-CN-YunyangNeural",
        "texts": {
            "idle.mp3": "爸爸，任务完成了，随时听候您的吩咐。",
            "thinking.mp3": "爸爸，我正在认真处理您交代的任务。",
            "thinking_long.mp3": "爸爸，这个问题有些复杂，我还在持续思考中，请耐心等待。",
            "waiting.mp3": "爸爸，这里需要您手动确认一下操作。",
            "error.mp3": "爸爸，运行时发生了一些错误，请查看日志。"
        }
    },
    "mama": {
        "voice": "zh-CN-XiaoxiaoNeural",
        "texts": {
            "idle.mp3": "妈妈，我把任务搞定了，乖乖等您吩咐哦！",
            "thinking.mp3": "妈妈，我正在努力动脑筋处理代码呢！",
            "thinking_long.mp3": "妈妈，这个问题有点复杂，我还在努力思考中，请稍等哦。",
            "waiting.mp3": "妈妈，这里有个操作需要您看一眼确认下哦！",
            "error.mp3": "妈妈，哎呀，系统报了个错，有点心塞！"
        }
    },
    "dongshizhang": {
        "voice": "zh-CN-YunyangNeural",
        "texts": {
            "idle.mp3": "董事长大人，各项任务已顺利完成，请指示。",
            "thinking.mp3": "董事长大人，我正在全力推进您的执行计划。",
            "thinking_long.mp3": "董事长大人，这个项目正在攻坚阶段，请您稍作等待。",
            "waiting.mp3": "董事长大人，有一项关键决策需要您的亲自审批。",
            "error.mp3": "董事长大人，系统遇到突发状况，已记录异常日志。"
        }
    },
    "guozhu": {
        "voice": "zh-CN-YunjianNeural",
        "texts": {
            "idle.mp3": "国主陛下，指令已执行完毕，微臣随时待命。",
            "thinking.mp3": "国主陛下，微臣正在竭尽全力处理该项事务。",
            "thinking_long.mp3": "国主陛下，此事干系重大，微臣仍在仔细斟酌，请陛下宽心稍候。",
            "waiting.mp3": "国主陛下，此项军国大事，还需陛下亲自定夺。",
            "error.mp3": "国主陛下，微臣办事不力，系统运行中出现了些许差错。"
        }
    },
    "huangshang": {
        "voice": "zh-CN-YunxiNeural",
        "texts": {
            "idle.mp3": "皇上，差事办妥了，奴才恭候您的旨意。",
            "thinking.mp3": "皇上，奴才正在马不停蹄地为您办事呢。",
            "thinking_long.mp3": "皇上，这差事有些棘手，奴才还在拼命琢磨，请皇上稍候片刻。",
            "waiting.mp3": "皇上，此处有一奏折，恳请皇上御批。",
            "error.mp3": "皇上，奴才该死，代码运行出了些岔子，请皇上降罪。"
        }
    }
}

async def generate():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")
    for profile, data in PROFILES.items():
        profile_dir = os.path.join(base_dir, profile)
        os.makedirs(profile_dir, exist_ok=True)
        
        voice = data["voice"]
        for filename, text in data["texts"].items():
            out_path = os.path.join(profile_dir, filename)
            if not os.path.exists(out_path) or filename == "thinking_long.mp3":
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(out_path)
                print(f"Generated {out_path} with text: {text}")

if __name__ == "__main__":
    asyncio.run(generate())

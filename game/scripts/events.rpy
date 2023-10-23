init python:
    import asyncio
    import aiohttp
    import json
    from dotenv import load_dotenv
    import openai
    import os
    import random
    import requests
    import math
    import time

    load_dotenv(".env")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    with open(config.basedir + "/game/prompt_templates.json", "r") as f:
        prompt = json.load(f)

    #TODO replace all this with a GUI in-game
    with open(config.basedir + "/IMPORTANT_CONFIG.txt", "r") as f:
        cs_config = f.read()

    def read_config(file_path):
        config_dict = {}
        with open(file_path, 'r') as file:
            for line in file:
                if "#" not in line:            
                    key, value = line.strip().split('=')
                    config_dict[key] = value
        return config_dict

    config_file_path = config.basedir + '/IMPORTANT_CONFIG.txt'
    cs_config = read_config(config_file_path)

    stable_token = cs_config['STABLE_TOKEN']
    vocal_token = cs_config['VOCAL_TOKEN']


    class ManageChat_Folders:
        def __init__(self):
            self.chat_path = "chats/"
            self.full_path = ""
            self.msg_history = "chat_history.json"
            self.saved_actions = "saved_actions.json"
            self.saved_data = {
                                "Scene": "club.png",
                                "Proceed": "First",
                                "head_sprite": "smile.png",
                                "leftside_sprite": "1l.png",
                                "rightside_sprite": "1r.png",
                                "zone": "None"
                            }
            self.chat_history = []
            

        
        def create_folder(self, name):
            """Creates specific folder in `chats` to store all
            realms.
            """
            path = self.chat_path+name

            i = 1
            while True:
                self.full_path = f"{config.basedir}/{path}_{i}"
                if not os.path.exists(self.full_path):
                    os.makedirs(self.full_path, mode=0o777)
                    break
                else:
                    i += 1
            
            return self.full_path


        def create_chat_history(self):
            """.json for logging chat history with monika & user"""
            try:
                with open(self.full_path+"/"+self.msg_history, "r") as f:
                    chat_history = json.load(f)

                self.chat_history = chat_history
                return chat_history
            except FileNotFoundError:
                with open(self.full_path+"/"+self.msg_history, "w") as f:
                    chat_history = []
                    json.dump(chat_history, f, indent=2)

                self.chat_history = chat_history
                return chat_history


        def create_world_history(self):
            """A .json for saving specific scenes such as:

            background, sprite, music and cinematic"""
            try:
                with open(self.full_path+"/"+self.saved_actions, "r") as f:
                    saved_data = json.load(f)

                self.saved_data = saved_data
                return saved_data
            except FileNotFoundError:
                with open(self.full_path+"/"+self.saved_actions, "w") as f:
                    saved_data = json.dump(self.saved_data, f, indent=2)

                self.saved_data = saved_data
                return saved_data








    class CheckData(ManageChat_Folders):
        def __init__(self, full_path):
            super().__init__()
            self.full_path = full_path
            self.ddlc_mode = {'justMonika': [0, 1], 'monikaZone': [2, 3]}

        def historyCheck(self, gamemode, chatmode):
            """
            Checks if chat_history is an empty list. If it is,
            it is overwrited with a prompt template

            Just Monika:
            0 is freechat
            1 is story mode

            ----

            Monika Zone:
            2 is freechat
            3 is story mode
            """
            try:
                self.chat_history[0]
            except IndexError:
                for m in self.ddlc_mode:
                    if m == gamemode:
                        with open(self.full_path+self.msg_history, "w") as f:
                            json.dump(prompt[self.ddlc_mode[m][chatmode]], f, indent=2)

                        with open(self.full_path+self.msg_history, "r") as f:
                            chat_history = json.load(f)
                        self.chat_history = chat_history
                        return chat_history
                            


        def usernameCheck(self):
            """
            Checks if the player has a registered username.
            If they do then it rewrites the first index of chat_history
            (aka the prompt template) to include it.

            This will make Monika address you by your name if
            necessary
            """
            if persistent.playerName != None:
                try:
                    prompt_name = self.chat_history[0]["content"].replace("<name>", persistent.playerName)
                    self.chat_history[0]["content"] = prompt_name

                    with open(self.full_path+self.msg_history, "w") as f:
                        json.dump(self.chat_history, f, indent=2)
                except IndexError:
                    return "File Currently Doesn't Exist"
                return prompt_name
            return "Username is not defined"




    class Convo(CheckData):
        def __init__(self, chat_history, full_path):
            super().__init__(full_path)
            self.full_path = full_path
            self.chat_history = chat_history
            self.head_sprite_dict = {'angry': 'monika serious.webp',
                            'annoyed': 'annoyed.png',
                            'blushing': 'monika blushing.png',
                            'concerned': 'curious.png',
                            'crying': 'cry.png',
                            'curious': 'curious.png',
                            'embarrassed': 'embarrassed.png',
                            'flabbergasted': 'monika flabbergasted.png',
                            'flirty': 'high.png',
                            'glad': 'glad.png',
                            'happy': 'smile.png',
                            'horrified': 'monika horrifiedYelling.png',
                            'nervous': 'nervous.png',
                            'playful frown': 'monika playfulFrown.webp', 
                            'playful smile': 'monika playfulSmile.webp', 
                            'really happy': 'smileOpenMouth.png', 
                            'resolve': 'annoyed_speaking.png', 
                            'sad': 'sad.webp', 
                            'scared': 'monika scared.png', 
                            'serious': 'monika serious.webp', 
                            'shocked': 'monika shocked.png', 
                            'worried': 'worried.png'
                            }
            self.leftside_sprite_dict = {'explain': '2l.png',
                            'relaxed': '1l.png',
                            'none': 'mtea.png',
                            }
            self.rightside_sprite_dict = {'explain': '2r.png',
                            'relaxed': '1r.png',
                            'none': 'mtea.png',
                            }
            self.bg_scenes = {"bedroom": "bedroom.png", "club": "club.png", "class": "class.png",
            "coffee shop": "coffee.jpg", "hallway": "hallway.png", "kitchen": "kitchen.png",
            "mc house": "house.png", "sayori's bedroom": "sayori_bedroom.png", "sayori bedroom": "sayori_bedroom.png", "sidewalk": "sidewalk.png",
            "user house": "house.png", "user's house": "house.png", "house": "house.png" }
            self.context_words = [
                "(done)", "(continue)", "[CONTENT]", "[MUSIC]", "[NARRATION]"
                ]
            self.NARRATION = False
            self.options = []
            self.proceed = self.saved_data["Proceed"]
            self.scene = self.saved_data["Scene"]
            self.head_sprite = self.saved_data["head_sprite"]
            self.leftside_sprite = self.saved_data["leftside_sprite"]
            self.rightside_sprite = self.saved_data["rightside_sprite"]
            self.zone = self.saved_data["zone"]
            self.voice_mode = False
            self.ai_art_mode = False
            self.continue_story = random.randint(1,7)


        @staticmethod
        def context_to_progress_story(msg):
            rng = random.randint(1,3)
            context = ""
            if rng == 1:
                context += " {Your next message should be a narration describing how the user is feeling}"
            elif rng == 2:
                context += " {Your next message should be a narration that pushes the story forward}"
            elif rng == 3:
                context += " {Your next message should be a narration explaining a possible way for the user to escape & how Monika would be really against that}"

            return msg + context



        def append_to_chat_history(self, role, msg):
            """Stores updated history of ai and user"""
            self.chat_history.append({"role": role, "content": msg})
            with open(self.full_path+self.msg_history, "w") as f:
                json.dump(self.chat_history, f, indent=2)

        def update_in_saved_actions(self, data, action):
            """Stores mood, visible chars, music in the current scene"""
            self.saved_data[data] = action
            with open(self.full_path+self.saved_actions, "w") as f:
                json.dump(self.saved_data, f, indent=2)


        def control_mood(self, mood):
            """Display different facial expressions"""
            emotions = ["angry", "blushing", "flabbergasted", "horrified",
                    "playful frown", "playful smile", "scared", "shocked", "serious",
                    "crying"]

            vocal_emotions = {
                "Happy": ["blushing", "playful smile", "flirty", "glad", "happy", "really happy"],
                "Sad": ["crying", "sad"],
                "Angry": ["angry"],
                "Surprise": ["shocked", "scared", "horrified", "flabbergasted"]
            }

            emo = "Neutral"

            for h in self.head_sprite_dict:
                if "[MOOD] "+h in mood:
                    self.update_in_saved_actions("head_sprite", self.head_sprite_dict[h])
                    self.head_sprite = self.head_sprite_dict[h]

                    # Adding tone to monika's voice
                    for vocal_list in vocal_emotions.items():
                        if h in vocal_list:
                            emo = vocal_list[0]
                            break

                    if h in emotions:
                        self.update_in_saved_actions("leftside_sprite", self.leftside_sprite_dict["none"])
                        self.leftside_sprite = self.leftside_sprite_dict["none"]

                        self.update_in_saved_actions("rightside_sprite", self.rightside_sprite_dict["none"])
                        self.rightside_sprite = self.rightside_sprite_dict["none"]

                        return emo

            if self.head_sprite in emotions:
                self.update_in_saved_actions("leftside_sprite", self.leftside_sprite_dict["none"])
                self.leftside_sprite = self.leftside_sprite_dict["none"]

                self.update_in_saved_actions("rightside_sprite", self.rightside_sprite_dict["none"])
                self.rightside_sprite = self.rightside_sprite_dict["none"]
                return emo               


            for l in self.leftside_sprite_dict:
                if "[BODY] "+l in mood:
                    self.update_in_saved_actions("leftside_sprite", self.leftside_sprite_dict[l])
                    self.leftside_sprite = self.leftside_sprite_dict[l]

            for rr in self.rightside_sprite_dict:
                if "[BODY] "+rr in mood:
                    self.update_in_saved_actions("rightside_sprite", self.rightside_sprite_dict[rr])
                    self.rightside_sprite = self.rightside_sprite_dict[rr]

            return emo


        def generate_ai_background(self, guide):
            """Generates unique AI background if it doesn't already exist in the bg folder"""
            ai_art_path = config.basedir + "/game/images/bg/"+ guide + ".png"
            if os.path.exists(ai_art_path):
                guide = guide + ".png"
                self.update_in_saved_actions("Scene", guide)
                self.scene = guide
                self.ai_art_mode = True
                return self.scene
            self.saved_data["scene_cache"].append(guide+".png")

            url = "https://stablediffusionapi.com/api/v3/text2img"

            payload = json.dumps({
            "key": stable_token,
            "prompt": "mdjrny-v4 style background anime scenery in " + guide + " hyperrealistic, highly detailed, cinematic lighting, stunningly beautiful, intricate, sharp focus, (professionally color graded), ((bright soft diffused light)), volumetric fog, trending on instagram, trending on tumblr, HDR 4K, 8K",
            "negative_prompt": "Disfigured, cartoon, blurry, nude, 1girl, 1boy, character",
            "width": "1024",
            "height": "1024",
            "samples": "1",
            "num_inference_steps": "31",
            "seed": None,
            "guidance_scale": 9,
            "safety_checker": "yes",
            "multi_lingual": "no",
            "panorama": "no",
            "self_attention": "no",
            "upscale": "no",
            "model_id": "midjourney",
            "scheduler": "DDPMScheduler",
            "vae": "sd-ft-mse",
            "lora": "more_details",
            "webhook": None,
            "track_id": None
            })

            headers = {
            'Content-Type': 'application/json'
            }

            guide = guide + ".png"
            response = requests.request("POST", url, headers=headers, data=payload, timeout=25)
            if response.status_code == 201 or response.status_code == 200:
                response_data = json.loads(response.text)
                with open(config.basedir + f"/game/images/bg/ai_imgs.json", "w") as f:
                    json.dump(response_data, f, indent=2)
                with open(config.basedir + f"/game/images/bg/ai_imgs.json", "r") as f:
                    ai_art = json.load(f)

                # Wait for "output" key to be returned by the API.
                # Would do this asynchronously but i've failed to do so atm.
                try: url = ai_art["output"][0]
                except (IndexError, KeyError):
                    time.sleep(55)
                    try: url = ai_art["output"][0]
                    except (IndexError, KeyError): return guide
                response = requests.get(url)

                with open(config.basedir + f"/game/images/bg/{guide}", "wb") as f:
                    f.write(response.content)

                self.update_in_saved_actions("Scene", guide)
                self.scene = guide
                self.ai_art_mode = True
            else:
                self.ai_art_mode = False

            return guide


        def control_scene(self, scene):
            """Display different scenes"""
            for s in self.bg_scenes:
                if f"[SCENE] {s}" in scene:
                    self.update_in_saved_actions("Scene", self.bg_scenes[s])
                    self.scene = self.bg_scenes[s]
                    return self.saved_data["Scene"]

            if "[SCENE]" in scene:
                scene = scene.split("[SCENE]")[1].split("[NARRATION]")[0].strip()
                return self.generate_ai_background(scene)



        def control_proceed(self, mode):
            """Determines if the user can respond & if the bg has changed"""
            self.update_in_saved_actions("Proceed", mode)
            self.proceed = mode
            return self.saved_data["Proceed"]




        def remove_context_words(self, reply):
            """Get rid of keywords and return a clean string"""
            if "[CINEMATIC]" not in reply and "[NARRATION]" not in reply and "[CONTENT]" not in reply:
                self.update_in_saved_actions("zone", "True")
                self.zone = "True"
            elif "[MOOD] crying" in reply:
                self.update_in_saved_actions("zone", "Zone")
                self.zone = "Zone"

            if "[NARRATION]" in reply:
                self.control_proceed("True") # User can now respond to AI
                self.NARRATION = True
            else:
                self.NARRATION = False

            reply = reply.split("[BODY]")[0].split("[MOOD]")[0]

            for ctx in self.context_words:
                reply = reply.replace(ctx, "")

            img = self.scene.replace(".png", "")
            reply = reply.replace("[SCENE] "+img, "")

            return reply


        def monika_speaks(self, reply, emote):
            """Convert Monika's text into vocals"""
            url = "https://app.coqui.ai/api/v2/samples/from-prompt/"
            payload = {
                "prompt": "An 18 year old girl with a sweet voice",
                "emotion": emote,
                "speed": 1,
                "text": reply
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": vocal_token
            }

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 201 or response.status_code == 200:
                self.voice_mode = True
                response_data = json.loads(response.text)
                with open(config.basedir +"/game/audio/vocals/aud.json", "w") as f:
                    json.dump(response_data, f, indent=2)
                with open(config.basedir +"/game/audio/vocals/aud.json", "r") as f:
                    aud = json.load(f)

                url = aud["audio_url"]
                response = requests.get(url)

                with open(config.basedir +"/game/audio/vocals/monika.wav", "wb") as f:
                    f.write(response.content)
            else:
                self.voice_mode = False
            return True



        def ai_response(self, msg, role="user"):
            """Gets ai generated text based off given prompt"""
            self.continue_story = random.randint(1,7)
            if "(init_end_sim)" in msg:
                self.update_in_saved_actions("zone", "Zone")
                self.zone = "Zone"
                return '...'

            # Log user input
            self.append_to_chat_history(role, msg)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=self.chat_history,
                temperature=0.6
                )
            
            ai_reply = response.choices[0].message.content
            # Log AI input
            self.append_to_chat_history('assistant', ai_reply)

            emote = self.control_mood(ai_reply)
            self.control_scene(ai_reply)
            final_res = self.remove_context_words(ai_reply)

            #TODO Should only run if player has voice enabled
            if self.NARRATION != True:
                #self.monika_speaks(final_res, emote=emote)
                pass
            return final_res








    #  Copied & Pasted Class from Official Doki Doki game (I am not a psychopath)
    class ParticleBurst:
        """Animates the particles in the main menu when the user first
        launches the game
        """
        def __init__(self, theDisplayable, explodeTime=0, numParticles=20, particleTime = 0.500, particleXSpeed = 3, particleYSpeed = 5):
            self.sm = SpriteManager(update=self.update)
            
            self.stars = [ ]
            self.displayable = theDisplayable
            self.explodeTime = explodeTime
            self.numParticles = numParticles
            self.particleTime = particleTime
            self.particleXSpeed = particleXSpeed
            self.particleYSpeed = particleYSpeed
            self.gravity = 240
            self.timePassed = 0
            
            for i in range(self.numParticles):
                self.add(self.displayable, 1)
        
        def add(self, d, speed):
            s = self.sm.create(d)
            speed = random.random()
            angle = random.random() * 3.14159 * 2
            xSpeed = speed * math.cos(angle) * self.particleXSpeed
            ySpeed = speed * math.sin(angle) * self.particleYSpeed - 1
            s.x = xSpeed * 24
            s.y = ySpeed * 24
            pTime = self.particleTime
            self.stars.append((s, ySpeed, xSpeed, pTime))
        
        def update(self, st):
            sindex=0
            for s, ySpeed, xSpeed, particleTime in self.stars:
                if (st < particleTime):
                    s.x = xSpeed * 120 * (st + .20)
                    s.y = (ySpeed * 120 * (st + .20) + (self.gravity * st * st))
                else:
                    s.destroy()
                    self.stars.pop(sindex)
                sindex += 1
            return 0

    #  Copied & Pasted Class from Official Doki Doki game
    class AnimatedMask(renpy.Displayable):
        
        def __init__(self, child, mask, maskb, oc, op, moving=True, speed=1.0, frequency=1.0, amount=0.5, **properties):
            super(AnimatedMask, self).__init__(**properties)
            
            self.child = renpy.displayable(child)
            self.mask = renpy.displayable(mask)
            self.maskb = renpy.displayable(maskb)
            self.oc = oc
            self.op = op
            self.null = None
            self.size = None
            self.moving = moving
            self.speed = speed
            self.amount = amount
            self.frequency = frequency
        
        def render(self, width, height, st, at):
            
            cr = renpy.render(self.child, width, height, st, at)
            mr = renpy.render(self.mask, width, height, st, at)
            mb = renpy.Render(width, height)
            
            
            if self.moving:
                mb.place(self.mask, ((-st * 50) % (width * 2)) - (width * 2), 0)
                mb.place(self.maskb, -width / 2, 0)
            else:
                mb.place(self.mask, 0, 0)
                mb.place(self.maskb, 0, 0)
            
            
            
            cw, ch = cr.get_size()
            mw, mh = mr.get_size()
            
            w = min(cw, mw)
            h = min(ch, mh)
            size = (w, h)
            
            if self.size != size:
                self.null = Null(w, h)
            
            nr = renpy.render(self.null, width, height, st, at)
            
            rv = renpy.Render(w, h)
            
            rv.operation = renpy.display.render.IMAGEDISSOLVE
            rv.operation_alpha = 1.0
            rv.operation_complete = self.oc + math.pow(math.sin(st * self.speed / 8), 64 * self.frequency) * self.amount
            rv.operation_parameter = self.op
            
            rv.blit(mb, (0, 0), focus=False, main=False)
            rv.blit(nr, (0, 0), focus=False, main=False)
            rv.blit(cr, (0, 0))
            
            renpy.redraw(self, 0)
            return rv

    def monika_alpha(trans, st, at):
        trans.alpha = math.pow(math.sin(st / 8), 64) * 1.4
        return 0
    
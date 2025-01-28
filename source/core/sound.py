from pygame import mixer

class Sound:

    def __init__(self):
        self.sounds: dict[str, mixer.Sound] = {}

    def initialize(self) -> None:
        mixer.init(44100, 16, 4, 4096)

        # List of sounds to load
        sound_files = {
            'playerHurt': './assets/sounds/playerHurt.ogg',
            'genericHurt': './assets/sounds/genericHurt.ogg',
            'confirmSound': './assets/sounds/confirmSound.ogg',
            'eventSound': './assets/sounds/eventSound.ogg',
            'spawnSound': './assets/sounds/spawnSound.ogg',
            'typingSound': './assets/sounds/typingSound.ogg'
        }

        # Load all sounds into the dictionary
        for key, file_path in sound_files.items():
            self.sounds[key] = mixer.Sound(file_path)


    def quit(self) -> None:
        mixer.quit()

    def play(self, sound_name: str) -> None:
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"[PLAY] Sound '{sound_name}' not found!")


    def stop(self, sound_name: str) -> None:
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
        else:
            print(f"[STOP] Sound '{sound_name}' not found!")

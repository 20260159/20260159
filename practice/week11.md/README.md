중간고사 제출 과정에서 player 파일이 절대 경로로 설정되어 있는 것을 검수하지 못하여 먼저 player 파일의

경로를 다른 파일들과 같이 절대 경로에서 상대 경로로 전환하고

원인 1: load\_player\_frames 함수 안의 잘못된 코드 (가장 유력함)

작성하신 코드의 load\_player\_frames 함수를 보면, 우리가 방금 전 resource\_path로 수정했던 코드 바로 밑에 예전 코드가 그대로 남아있습니다.



❌ 현재 문제가 되는 부분:



Python

def load\_player\_frames():

&#x20;   image\_file\_path = resource\_path("./assets/sprites/player.png")

&#x20;   image\_name = "player.png"  # <- (문제) 쓸데없는 코드

&#x20;   image\_file\_path = os.path.join(base\_path, image\_name) # <- (핵심 문제) base\_path라는 변수가 없어서 
   여기서 게임이 크래시(Crash) 납니다!
라는 내용이 발생하여 바로 수정하여 정상 작동 되게 되었습니다.

그리고 pyinstaller를 thonny에서 다운 받고

resource\_path를 asset 코드  앞에 붙여 exe에서도 작동되게 설정하였습니다. 

그리고 터미널에서 pyinstaller --onefile "ai project.py"를 설정하여 dist와 build 폴더를 생성하고

이후 pyinstaller --onefile --windowed "ai project.py"로 터미널 창을 숨기고
pyinstaller --onefile --windowed --add-data "assets;assets" --name=MyGame "ai project.py"로

에셋을 포함시키고 이름 지정을 하게되었습니다.


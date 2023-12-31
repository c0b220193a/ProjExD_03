import os
import random
import sys
import time
import math

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
NUM_OF_BOMBS = 5  # 爆弾の数


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
        self.imgs = {  # 0度から反時計回りに定義
            (+5, 0): img,  # 右
            (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-5, 0): img0,  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        # self.img = pg.transform.flip(  # 左右反転
        #     pg.transform.rotozoom(  # 2倍に拡大
        #         pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 
        #         0, 
        #         2.0), 
        #     True, 
        #     False
        # )
        self.img = self.imgs[(+5, 0)]  # 右向きこうかとんをデフォ画像にする
        self.rct = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5,0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):  # なにもキーが押されていなくなかったら
            self.img = self.imgs[tuple(sum_mv)] 
        screen.blit(self.img, self.rct)
        if not(sum_mv[0] == 0 and sum_mv[1] == 0): 
            self.dire = (sum_mv[0], sum_mv[1])


class Bomb:
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    # directions = [-5, +5]
    """
    爆弾に関するクラス
    """
    def __init__(self):
        """
        爆弾円Surfaceを生成する
        """
        rad = random.randint(10, 100)
        self.img = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # Bomb.colors
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = random.choice([-5, +5]), random.choice([-5, +5])

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    def __init__(self, bird: Bird):
        self.img = pg.image.load(f"{MAIN_DIR}/fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery   # こうかとんの中心座標を取得
        self.rct.centerx = bird.rct.centerx+bird.rct.width/2
        self.vx, self.vy = bird.dire  # こうかとんが向いている方向を取得
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.img = pg.transform.rotozoom(self.img, angle, 1.0)
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.centerx = bird.rct.centerx + bird.rct.width / 2 + self.rct.width * self.vx / 5
        self.rct.centery = bird.rct.centery + self.rct.height * self.vy / 5

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    def __init__(self, screen):  # screenを引数に追加
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.txt = 0  # txtを追加
        self.screen = screen  # screenを追加
        self.img = self.font.render("スコア:" + str(self.txt), 0, (0, 0, 255))
        self.img_rect = self.img.get_rect()
        self.img_rect.centerx = 100
        self.img_rect.centery = 850

    def update(self):
        self.img = self.font.render("スコア:" + str(self.txt), 0, (0, 0, 255))
        self.screen.blit(self.img, self.img_rect)

class Explosion:
    def __init__(self, center, life=30):
        self.imgs = [
            pg.image.load("ex03/fig/explosion.gif"),
            pg.transform.flip(pg.image.load("ex03/fig/explosion.gif"), True, False),
            pg.transform.flip(pg.image.load("ex03/fig/explosion.gif"), False, True),
            pg.transform.flip(pg.image.load("ex03/fig/explosion.gif"), True, True)
        ]
        self.img_idx = 0
        self.img = self.imgs[self.img_idx]
        self.rct = self.img.get_rect()
        self.rct.center = center
        self.life = life

    def update(self):
        self.life -= 1
        if self.life > 0:
            self.img_idx = (self.img_idx + 1) % len(self.imgs)
            self.img = self.imgs[self.img_idx]


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    # BombインスタンスがNUM個並んだリスト
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS)]  
    beams = []
    score = Score(screen)
    explosions = []

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:  # スペースキーが押されたら
                beams.append(Beam(bird))  # ビームインスタンスの生成
        
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return

        for i, bomb in enumerate(bombs):
            for j, beam in enumerate(beams):
                if beam is not None and bomb is not None:
                    if beam.rct.colliderect(bomb.rct):
                        # 爆発位置を爆弾の中心に設定し、Explosionインスタンスを生成
                        explosion = Explosion(bomb.rct.center)
                        explosions.append(explosion)
                        beams[j] = None
                        bombs[i] = None
                        score.txt += 1
                        bird.change_img(6, screen)

        # beamが画面の中にいるかどうかの判定
        for i, beam in enumerate(beams): 
            if beam is not None:
                if beam.rct.left <= 0 or beam.rct.right >= WIDTH or beam.rct.top <= 0 or beam.rct.bottom >= HEIGHT:
                    beams[i] = None
        # Noneでない爆弾だけのリストを作る 
        bombs = [bomb for bomb in bombs if bomb is not None]
        # Noneでないビームだけのリストを作る
        beams = [beam for beam in beams if beam is not None]
        # lifeが0より大きいExplosionインスタンスだけのリストにする
        explosions = [explosion for explosion in explosions if explosion.life > 0]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for bomb in bombs:
            bomb.update(screen )
        for beam in beams:
            beam.update(screen)
        for explosion in explosions:
            explosion.update()       
            screen.blit(explosion.img, explosion.rct)
        score.update()
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
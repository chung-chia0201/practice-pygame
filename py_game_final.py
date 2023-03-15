 # 增加初始畫面
from lib2to3.pytree import convert
import winsound,os,random,sys
import pygame as pg
from pyparsing import White  

FPS = 60
WIDTH = 901
HEIGHT = 630

N=0 #死亡次數

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
JOCELYN = (255, 228, 225)
RED=(255,0,0)
YELLOW=(255,255,0)
BLACK=(0,0,0)
# 遊戲初始化and創建視窗
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))  # 遊戲視窗大小
pg.display.set_caption("peko_shot")
clock = pg.time.Clock()

#載入圖片
background_img=pg.image.load(os.path.join("game_spacewar","picture_for_game","giant_carrot.png")).convert()
player_img=pg.image.load(os.path.join("game_spacewar","picture_for_game","peko.png")).convert()
# rock_img=pg.image.load(os.path.join("game_spacewar","picture_for_game","human.png")).convert()
bullet_img=pg.image.load(os.path.join("game_spacewar","picture_for_game","carrot.png")).convert()
rock_imgs=[]
for i in range(1,7):    
    # image = pg.image.load(os.path.join("game_spacewar","picture_for_game",f"rock{i}.png")).convert()
    # image1 = pg.transform.scale(image,(100,100)).convert()                        #更改石頭的大小
    # rock_imgs.append(image1)
    rock_imgs.append(pg.image.load(os.path.join("game_spacewar","picture_for_game",f"rock{i}.png")).convert())   #在字串裡面使用變數的方法

#載入動畫
expl_anim={}
expl_anim['lg']=[]
expl_anim['sm']=[]
for i in range(2):        #放入爆炸動畫
    expl_img=pg.image.load(os.path.join("game_spacewar","picture_for_game",f"expl{i}.png")).convert()
    expl_img.set_colorkey(WHITE)
    expl_anim['lg'].append(pg.transform.scale(expl_img,(75,75)))
    expl_anim['sm'].append(pg.transform.scale(expl_img,(30,30)))

power_imgs={}
power_imgs['medicine']=pg.image.load(os.path.join("game_spacewar","picture_for_game","medicine.png")).convert()
power_imgs['lightning']=pg.image.load(os.path.join("game_spacewar","picture_for_game","lightning.png")).convert()

#載入音樂
shoot_sound=pg.mixer.Sound(os.path.join("game_spacewar","music_for_game","shoot_good.mp3"))
expl_sounds=[pg.mixer.Sound(os.path.join("game_spacewar","music_for_game","expl_good0.mp3")),
             pg.mixer.Sound(os.path.join("game_spacewar","music_for_game","expl_good1.mp3"))
              ]
#背景音樂
pg.mixer.music.load(os.path.join("game_spacewar","music_for_game","background.ogg"))


font_name=os.path.join("game_spacewar","font.ttf")         #載入顯示分數的字體
def draw_text(surf,text,size,x,y):        #顯示分數 
    font=pg.font.Font(font_name,size)
    text_surface=font.render(text,True,WHITE)  #第二個參數使用TRUE,會使字體比較滑順
    text_rect=text_surface.get_rect()
    text_rect.x=x
    text_rect.top=y
    surf.blit(text_surface,text_rect)

def new_rock():      #生成新的隕石
    r=Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf,hp,x,y):  #畫血條
    if hp<0:
        hp=0
        # hp=100
    BAR_LENGTH=300         #血條長度
    BAR_HEIGHT=20
    fill=(hp/100)*BAR_LENGTH  #填滿多少血條 
    outline_rect=pg.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)  #顯示外框(X座標,y座標,長度,高度)
    fill_rect=pg.Rect(x,y,fill,BAR_HEIGHT)
    pg.draw.rect(surf,JOCELYN,fill_rect)  #畫裡面
    pg.draw.rect(surf,BLACK,outline_rect,2)    #畫外

def draw_gameover(surf,text,size,x,y,colar):        #顯示失敗 
    font=pg.font.Font(font_name,size)
    text_surface=font.render(text,True,colar)  #第二個參數使用TRUE,會使字體比較滑順
    text_rect=text_surface.get_rect()
    text_rect.x=x
    text_rect.top=y
    surf.blit(text_surface,text_rect)

def draw_init():
    screen.blit(background_img,(0,0))
    draw_text(screen,"紅蘿蔔大戰!",64,WIDTH/2,HEIGHT/4)
    draw_text(screen,"← →移動飛船  空白鍵發射子彈",22,WIDTH/2,HEIGHT/2)
    draw_text(screen,"按任意鍵開始遊戲",18,WIDTH/2,HEIGHT*3/4)
    pg.display.update()
    waiting=True
    while waiting:
        clock.tick(FPS)
        #取得輸入
        for event in pg.event.get():
            if event.type == pg.QUIT:         #如果按叉叉就把遊戲關掉
                pg.quit()
                return True
            elif event.type == pg.KEYUP:      #如果按鍵盤
                waiting=False
                return False


class Player(pg.sprite.Sprite):          #飛船
    def __init__(self):                  # https://www.youtube.com/watch?v=61eX0bFAsYs&t=1325s  23:00
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(player_img,(50,50))
        self.image.set_colorkey(BLACK)     #去除背景
        self.rect = self.image.get_rect()
        self.radius=25                     #設定碰撞半徑
        # pg.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom=HEIGHT-10
        self.speedx=8
        self.health=100

    def update(self):
        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_RIGHT]:                #按住鍵盤向右鍵就會往右移
            self.rect.x += self.speedx
        if key_pressed[pg.K_LEFT]:                 #按住鍵盤向右鍵就會往右移
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:                #跑到螢幕最右邊會卡住
            self.rect.right = WIDTH
        if self.rect.left < 0:                     #跑到螢幕最左邊會卡住
            self.rect.left = 0

    def shoot(self):
        bullet=Bullet(self.rect.centerx,self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        pg.mixer.music.set_volume(1)  
        shoot_sound.play()
        
class Rock(pg.sprite.Sprite):  #石頭
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_ori=random.choice(rock_imgs)                                #再儲存一張,每次都用原圖轉
        self.image_size=random.randint(50,150)
        self.image_ori = pg.transform.scale(self.image_ori,(self.image_size,self.image_size)).convert()
        self.image_ori.set_colorkey(WHITE)            #去背
        self.image=self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius=self.rect.width/2             #設定碰撞判斷半徑
        # pg.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy=random.randrange(2, 10)
        self.speedx=random.randrange(-3, 3)
        self.total_degree=0
        self.rot_degree=random.randrange(-3, 3)                    #石頭轉動的角度

    def rotate(self):
        self.total_degree+=self.rot_degree
        self.total_degree=self.total_degree%360
        self.image=pg.transform.rotate(self.image_ori,self.total_degree)
        center=self.rect.center
        self.rect=self.image.get_rect()
        self.rect.center= center

    def update(self):
        self.rotate()
        self.rect.y+=self.speedy
        self.rect.x+=self.speedx
        if self.rect.top>HEIGHT or self.rect.left>WIDTH or self.rect.right<0:
            self.rect.centerx = random.randrange(0, WIDTH-self.rect.width)
            self.rect.centery = random.randrange(-100, -40)
            self.speedy=random.randrange(2, 10)
            self.speedx=random.randrange(-3, 3)

class Bullet(pg.sprite.Sprite):  #子彈
    def __init__(self,x,y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(bullet_img,(100,100))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy=-10

    def update(self):
        self.rect.y+=self.speedy
        if self.rect.bottom<0:
            self.kill()            #跑出畫面的子彈就刪掉    
                 
class Explosion(pg.sprite.Sprite):  #爆炸動畫
    def __init__(self,center,size):
        pg.sprite.Sprite.__init__(self)
        self.size=size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame=0
        self.last_update=pg.time.get_ticks()
        self.frame_rate=50              #動畫更新速率

    def update(self):
        now=pg.time.get_ticks()
        if now-self.last_update>self.frame_rate:
            self.last_update=now
            self.frame+=1
            if self.frame==len(expl_anim[self.size]):
                self.kill()
            else:
                self.image=expl_anim[self.size][self.frame]
                center=self.rect.center
                self.rect=self.image.get_rect()
                self.rect.center=center

all_sprites = pg.sprite.Group()
rocks=pg.sprite.Group()
bullets=pg.sprite.Group()
player = Player()
all_sprites.add(player)
rock=Rock()
all_sprites.add(rock)
for i in range(8):
    new_rock()
score=0
pg.mixer.music.play(-1)       #背景音樂
pg.mixer.music.set_volume(0.2)
# 遊戲迴圈
show_init=True
running = True
while running: 
    if show_init:
        close=draw_init()
        if close:
            break
        show_init=False
    clock.tick(FPS)  # 一秒最多運行FPS次
    # 取得輸入
    for event in pg.event.get():
        if event.type == pg.QUIT:         #如果按叉叉就把遊戲關掉
            running = False
        elif event.type==pg.KEYDOWN:      #如果按鍵盤
            if event.key==pg.K_SPACE:
               player.shoot()
            elif event.key==pg.K_ESCAPE:
                running = False

    # 更新遊戲
    all_sprites.update()
    hits=pg.sprite.groupcollide(rocks,bullets,True,True) #判斷子彈和石頭有沒有碰撞,後面兩個參數分別代表要不要消除
    for hit in hits:
        new_rock()
        pg.mixer.music.set_volume(0.5) 
        random.choice(expl_sounds).play()
        score+=int(hit.radius)
        expl=Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        
    hits=pg.sprite.spritecollide(player,rocks,True,pg.sprite.collide_circle)   #最後參數表示改採用圓形判斷碰撞
    for hit in hits:
        new_rock()
        player.health-= hit.radius/3
        expl=Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        if player.health<=0:
            N+=1
            winsound.Beep(800,200)
            player.health=100                    
            # running=False
             
        
    # 畫面顯示
    screen.fill(BLACK)  # (R,G,B)==調色盤(紅,綠,藍) 範圍為0~255
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen)
    if N>0:
        draw_gameover(screen,str('Number of deaths:'),30,WIDTH-310,HEIGHT*7/8,WHITE) 
    draw_gameover(screen,str(N),30,WIDTH-40,HEIGHT*7/8,WHITE)
    draw_text(screen,str(score),50,WIDTH/2,10)
    draw_health(screen,player.health,10,20)
    pg.display.update()

pg.quit()

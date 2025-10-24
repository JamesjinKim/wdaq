import sys
import os
import time
import argparse
#import smbus            #I2C 제어용
import spidev           # SPI 통신을 위한 모듈
import RPi.GPIO as GPIO # GPIO 제어를 위한 모듈

from gpiozero import LED
import datetime

import gpiod
import threading

# 사용자 정의 콜백 함수
def gpio_event_callback(pin, edge):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state = "눌림(LOW)" if edge == "falling" else "해제(HIGH)"
    print(f"[{timestamp}] GPIO {pin} 상태 변경 감지 → {state}")

# GPIO 입력 감시 스레드 함수
def monitor_gpio_interrupt(pin, callback):
    chip = gpiod.Chip("gpiochip0")
    line = chip.get_line(pin)
    line.request(consumer="gp40-monitor", type=gpiod.LINE_REQ_EV_BOTH_EDGES)

    last_event_time = 0  # 마지막 이벤트 발생 시각
    debounce_time = 0.2  # 디바운스 시간 (초) → 필요시 조정 가능

    while True:
        line.event_wait()
        event = line.event_read()
        current_time = time.time()

        if current_time - last_event_time > debounce_time:
            edge = "rising" if event.type == gpiod.LineEvent.RISING_EDGE else "falling"
            callback(pin, edge)
            last_event_time = current_time

# 전역변수
rstr = ["±10V","±5V","±2.5V","±1.25V","±0.5V","0-10V","0-5V","0-2.5V","0-1.25V","0-20mA","NONE"]   # 전압 범위 문자열 목록
chn  = [      0,     1,       2,        3,      11,      5,     6,       7,       15,       6,     0]   # 입력 범위 설정을 위한 레지스터 값 테이블
chu  = [  0x800, 0x800,   0x800,    0x800,   0x800,  0x000, 0x000,   0x000,    0x000,   0x000, 0x000]   # 실제 값 변환을 위한 보정값 (0x800 바이폴라, 0x000 유니폴라)
chm  = [   5.00,  2.50,    1.25,    0.625,  0.3125,   2.50,  1.25,   0.625,   0.3125,    5.00,   0.0]   # 실측값 변환을 위한 곱셈 계수 (1LSB당 [mV] 또는 [uA])
chr  = [0,0,0,0,0,0,0,0]         # ch0-7의 입력 범위 초기값
adalarm = 0                      # AD 알람 상태 (0 비활성, 1 활성)
adach = 0                        # AD 알람 발생 채널 (bit0-7 ch0-7, bit DIN)
adadt = 0                        # 디지털 입력 감지 시 ADC ch0 값 
ADCS = 8                         # AD SPI CS 핀으로 사용할 GPIO 번호 8

DOUT = 12                   # 디지털 출력 GPIO12 (JP8 Default)  GPIO14(JP7)
DIN  = 13                   # 디지털 입력 GPIO13 (JP6 Default)  GPIO15(JP5)

# RPi-GP40 초기 설정 
def init_GP40():
    GPIO.setmode(GPIO.BCM)                                # Broadcom 핀 번호 방식 사용
    GPIO.setwarnings(False)
    GPIO.setup(ADCS, GPIO.OUT, initial=GPIO.HIGH)         # ADCS를 GPIO 핀으로 제어 (초기 HIGH)
    # GPIO.setup(27,   GPIO.OUT, initial=GPIO.HIGH )      # GPIO 27번 전원 제어 제거 (입력 전용 사용)
    GPIO.setup(DOUT, GPIO.OUT, initial=GPIO.LOW )         # DOUT 핀 출력 설정 (LOW = OFF)
    GPIO.setup(DIN,  GPIO.IN,  pull_up_down=GPIO.PUD_OFF) # DIN 핀 입력 설정 (풀업풀다운 미사용)
    time.sleep(0.5)                                       # 전원 안정화 대기 

# ADC와 SPI 데이터 전송 
# 2020-05-27 이후 라즈베리파이 os에서 SPI CS 핀에 불필요한 'L' 펄스가 발생하는 문제 해결을 위해 GPIO 제어 방식으로 변경 (2020-10-23)
def xfer_spiadc( wd ):
    GPIO.output(ADCS, 0)         # SPI CS0='L' 설정. (GPIO 핀으로 제어)
    rd = spi.xfer(wd)
    GPIO.output(ADCS, 1)         # SPI CS0='H' 설정.
    return rd

# 지정한 채널의 입력 범위 설정 레지스터 값 설정 - 레지스터 값 쓰기
def set_adrange(ch, r):
    wdat = [((5+ch)<<1)|1, r, 0x00, 0x00]     # 채널의 입력 범위 설정 
    rdat = xfer_spiadc(wdat)

# 지정한 채널의 입력 범위 설정 레지스터 값 가져오기 - 레지스터 값 읽기
def get_adrange(ch):
    wdat = [((5+ch)<<1)|0, 0x00, 0x00, 0x00]  # 채널의 입력 범위 조회 
    rdat = xfer_spiadc(wdat)
    return rdat[2]

# 지정한 채널의 AD 변환 데이터 가져오기 - 데이터 읽기 
def get_addata(ch):
    wdat = [0xc0+(ch<<2), 0x00, 0x00, 0x00]   # 채널 AD 변환 요청
    rdat = xfer_spiadc(wdat)                  # 채널 지정 
#   time.sleep(0.1)
    rdat = xfer_spiadc(wdat)                  # AD 데이터 가져오기
    adat = (rdat[2]<<4)+(rdat[3]>>4)          # AD 변환 값 계산 (상위 8비트와 하위 4비트 결합)
    return adat

# ch0-7의 AD 변환 실행 및 결과 표시 
def print_adc(intv, cnt):                     # intv 표시 간격 [sec] cnt 표시 횟수 [회]
    global adach
    for i in range(cnt):                      # 표시 횟수만큼 반복
        for adc in range(8):                  # ch0-7에 대해 
            if( chr[adc]>9 ):                 # 유효하지 않은 채널이면、
                print("%8s ch%d        [---]" % (rstr[chr[adc]], adc) )    # AD 변환 없음 
            else:                             # 유효한 채널이라면、
                adat = get_addata(adc)        # ch 'adc'에 대해 AD 변환 실행 
                volt = (adat-chu[chr[adc]])*chm[chr[adc]]/1000  # 입력 범위에 따른 실제 값 계산 = (AD변환값 - 보정값) x 곱셈 계수
                print("%8s ch%d%8.4f[%03X]" % (rstr[chr[adc]], adc, volt, adat) )  # 결과 표시
        if( adach == 0 ):                     # 알람이 없으면、
            if( cnt>1 ):                      # 여러 번이면、
                print("%5d/%d" %(i+1, cnt))   # 진행 횟수 표시 
            if( i<(cnt-1) ):
                time.sleep(intv)              # 표시 간격 대기
                sys.stdout.write("\033[9F")   # 커서를 9행 위로 이동
                sys.stdout.flush()
        else:                                 # 알람이 있으면、
            print( "알람 검지! ch7-0{:08b}  ".format(adach), end="" ) 
            wdat = [(0x11<<1)|1, 0x00, 0x00, 0x00]
            rdat1 = xfer_spiadc(wdat)         # 알람 ch0-3 변화 레지스터 읽기
            wdat = [(0x12<<1)|1, 0x00, 0x00, 0x00]
            rdat2 = xfer_spiadc(wdat)         # 알람 ch0-3 상태 레지스터 읽기
            wdat = [(0x13<<1)|1, 0x00, 0x00, 0x00]
            rdat3 = xfer_spiadc(wdat)         # 알람 ch4-7 변화 레지스터 읽기 
            wdat = [(0x14<<1)|1, 0x00, 0x00, 0x00]
            rdat4 = xfer_spiadc(wdat)         # 알람 ch4-7 상태 레지스터 읽기 
            print( " ch0-3Trip%02XActive%02X, ch4-7Trip%02XActive%02X " %
                ( rdat1[2], rdat2[2], rdat3[2], rdat4[2] ) )
            adach = 0                         # 알람 상태 클리어
            break                             # 계측 중단 

    print()

# 알람 설정 
def set_adalarm(ch, hist, hth, lth):          # ch 알람 설정 채널, hist 히스테리시스, hth,lth 상한하한 임계값 
    reg = 0x15+(ch*5)                         # 알람 레지스터 베이스 주소 (ch0=0x15 ～ ch7=0x38)
    reg = (reg<<1)|1                          # 레지스터에 쓰기 위한 주소 변환 
    wdat = [reg, hist<<4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 히스테리시스 설정 
    wdat = [reg+2, hth>>4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 상한 임계값 상위 8bit 설정
    wdat = [reg+4, (hth&0x0f)<<4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 상한 임계값 하위 4bit 설정
    wdat = [reg+6, lth>>4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 하한 임계값 상위 8bit 설정
    wdat = [reg+8, (lth&0x0f)<<4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 하한 임계값 하위 4bit 설정

# 알람 활성화 
def ena_adalarm(en):                          # 0 알람 비활성, 1 알람 활성 
    global adalarm
    wdat = [(0x03<<1)|1, 0x00, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 피처 셀렉트 레지스터 읽기
    wdat = [(0x03<<1)|1, (rdat[2]&0xef)|((en&1)<<4), 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 알람 기능 활성/비활성 설정
    adalarm = en&1                            # 알람 상태 저장

# 알람 콜백 함수 
def callback_adalarm(din):
    global adach
    global adadt
    
    # 1.
    wdat = [(0x10<<1)|1, 0x00, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 알람 원인 레지스터 읽기 
    # 2.
    if( rdat[2]==0 ):                         # 알람 없음 = DIN 입력 (High→Low 변화) 감지 
        adach = 0x100                         # bit8 DIN
        adadt = get_addata(0)                 # ch0의 AD 변환값 저장 
        print("디지털 입력 DIN(H → L변화) 감지! ch0[%03X]" % adadt )    # 검지 시 ch0 ADC 데이터 표시 
    # 3.
    else:
        adach = rdat[2]                       # bit7-0 ch7-0

# ------------------ 메뉴 실행 부분 ------------------ #
# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                prog='sampleGp40.py',   # 프로그램 파일명 
                usage='메뉴 형식으로 RPi-GP40 제어', # 사용 방법  
                description='인수를 지정하여 직접 실행 가능',
                epilog=     '--------------------------------------------------------------------------',
                add_help=True,
                )
    # 인수 
    parser.add_argument('-r', '--range', metavar='[R]'  , nargs=8, 
                        help='[R]= 0±10V 1±5V 2±2.5V 3±1.25V 4±0.5V 5:0-10V 6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA 以外無効 ' + 
                             '채널 0-7의 입력범위(0-9)를 지정. ex -r 0 0 5 5 6 6 6 9')
    parser.add_argument('-t', '--time',  metavar='[T]'   , nargs=1, 
                        help='[T]= AD 변환 간격(1-1000)[초] 지정. ex -t 1')
    parser.add_argument('-c', '--cnt',  metavar='[C]'   , nargs=1, 
                        help='[C]= AD 변환 횟수(1-1000)[회] 지정. ex -c 100')
    args = parser.parse_args()  # 인수 확인 

    interval = 0                # 표시 간격 (0: 1회, 1～1000[초])

    try:
        # 인수 얻기 
        if( args.range ):           # 입력 범위 
            for adc in range(8):
                chr[adc] = int(args.range[adc], 16)
        if( args.time ):            # AD 변환 간격
            interval = int(args.time[0],10)
        if( args.cnt ):             # AD 변환 횟수 
            cnt = int(args.cnt[0],10)

        # RaspberryPi SPI 기능 설정 
        spi  = spidev.SpiDev()      # RPi-GP40는 SPI 사용
        spi.open(0, 0)              #  SPI0, CEN0로 오픈 
        spi.no_cs = True            #  CS는 spidev가 아닌 GPIO로 제어 
        spi.mode = 1                #  SPI 클럭 설정 CPOL=0 (정논리), CPHA=1 (Hihg-Low에서 데이터 읽기)
        spi.max_speed_hz = 10000000 #  SPI 최대 클럭 주파수 (17MHz 지정)
                                    #   단、2018년 4월 당시 커널에서는 지정값보다 실제 주파수가 낮아질 수 있음  
                                    #   예) 17MHz→10.5MHz, 10MHz→6.2MHz, 8MHz→5MHz, 28MHz→15.6MHz
         

        # RPi-GP40 초기 설정 
        init_GP40()

        # ------------------ gpiod 기반 GPIO 인터럽트 스레드 시작 ------------------ #
        input_pins = [5, 17, 22, 27]  # GPIO 27번도 입력으로 사용
        for pin in input_pins:
            t = threading.Thread(target=monitor_gpio_interrupt, args=(pin, gpio_event_callback), daemon=True)
            t.start()
        # -------------------------------------------------------------------------- #

        # 입력 범위 설정 
        for adc in range(8):
            if( chr[adc]<=9 ):      # 유효한 채널이면, 
                set_adrange(adc, chn[chr[adc]])     # ch 'adc'의 입력 범위 설정 

        # 인수에 따른 직접 실행 형식 
        if( interval != 0 ):        # 인수 지정이 있으면, 
            print_adc(interval,cnt) # interval 간격으로 cnt회 AD 변환값 표시 
            # GPIO.output(27, False)  # GPIO 27번 전원 제어 제거 (입력 전용 사용)
            GPIO.cleanup()
            sys.exit()

        ## ----- INPUT ----- 
                
        # 모드 중복 설정 방지
        # GPIO 모드 설정
        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # 인수 없이 메뉴 실행 형식 
        while True:

            # 각 채널의 입력 범위 설정 값 표시 
            print("ch렌즈= 0:%s  1:%s  2:%s  3:%s  4:%s  5:%s  6:%s  7:%s" % 
                (rstr[chr[0]], rstr[chr[1]], rstr[chr[2]], rstr[chr[3]], rstr[chr[4]], rstr[chr[5]], rstr[chr[6]], rstr[chr[7]]) )

            # 메뉴 표시 
            menu = input("0-7: ch 범위 설정  a: 단일 AD 변환  b: 연속 AD 변환  c: 알람  d: 디지털 IO  e: 종료: ")
            c = int(menu, 16)

            # '0'～'7' ch 입력 범위 설정 
            if( (c>=0)and(c<=7) ):  
                print("입력 범위 0:±10V  1:±5V  2:±2.5V  3:±1.25V  4:±0.5V  5:0-10V  6:0-5V  7:0-2.5V  8:0-1.25V  9:0-20mA  a: 무효")
                d = input("ch%d 입력 범위: " % c )
                chr[c] = int(d, 16)
                if( chr[c] <= 9 ):
                    set_adrange(c, chn[chr[c]])     # ch 'c'의 입력 범위 설정 

            # 'a' 단일 AD 변환
            if( c==10 ):            
                print_adc(0, 1)     # 간격 0으로 1회 AD 변환값 표시

            # 'b' 연속 AD 변환 
            if( c==11 ):            
                i = input(" 연속 AD 변환 간격 (1-1000[초]): ")
                interval = int(i)
                i = input(" 연속 AD 변환 횟수 (1-1000[회]): ")
                cnt = int(i)
                print_adc(interval, cnt) # interval 간격으로 cnt회 AD 변환값 표시

            # 'c' 알람
            if( c==12 ):            
                i = input(" 알람 0-7: 활성 [ch], a: 비활성: ")
                if( i=='a' ):       # 비활성이면、
                    ena_adalarm( 0 )                    # 알람 비활성화 
                    if( adalarm==1 ):
                        GPIO.remove_event_detect(DIN)   # ALARM 인터럽트 해제
                    print("알람 해제되었습니다.")
                else:               # 알람 설정 값 입력 
                    ch = int(i) & 0x07
                    i = input(" 히스테리시스 (0-15[LSB]): ")
                    hist = int(i) & 0x0f
                    i = input(" 상한 임계값 (HEX) 000-FFF: ")
                    hth = int(i,16) & 0xfff
                    i = input(" 하한 임계값 (HEX) 000-FFF: ")
                    lth = int(i,16) & 0xfff
                    set_adalarm(ch, hist, hth, lth)     # 알람 설정
                    if( adalarm==1 ):
                        GPIO.remove_event_detect(DIN)   # ALARM 인터럽트 해제
                    adach = 0                           # 알람 클리어
                    GPIO.add_event_detect(DIN, GPIO.FALLING, callback=callback_adalarm, bouncetime=200)  # ALARM,DIN 인터럽트 콜백 설정 
                    ena_adalarm( 1 )                    # 알람 활성화
                    print("알람 활성화되었습니다. 연속 AD 변환 중 알람 검지 시 계측이 중단됩니다.")
                print()

            # 'd' 디지털 입출력 
            if( c==13 ):   
                if not GPIO.getmode():  # 이미 설정된 경우 중복 설정 방지
                    GPIO.setmode(GPIO.BCM)

                #GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 핀 설정
                #GPIO.add_event_detect(17, GPIO.FALLING, callback=input_callback_adalarm, bouncetime=200)  # 감지 등록


                mode = input(" 입력: i, 출력: o, 돌아가기: a: ")
                if ( mode == 'a' ):
                    continue    # 상위 메뉴로 돌아감
                
                ## ----- OUTPUT -----
                elif ( mode == 'o'): 
                    # LED 객체 생성
                    DIN_1 = LED(23)   # (GPIO 23번 핀 사용)
                    DIN_2 = LED(24)   # (GPIO 24번 핀 사용)
                
                    # 무한반복: 사용자로부터 입력을 받아 LED 제어
                    while True:
                        pin_number_input = input("Enter LED PIN NUMBER 23 or 24, 돌아가기: a: ")
                        if (pin_number_input=='a'):
                            break   # LED 핀 선택으로 돌아감
                        elif pin_number_input not in ['23', '24']:
                            print("23 또는 24를 입력하세요.")
                            continue

                        # 선택된 LED 객체 결정
                        if pin_number_input == '23':
                            selected_pin = DIN_1
                        else:   # pin_number_input == '24'
                            selected_pin = DIN_2

                        # 내부 루프: 선택한 LED에 대해 계속해서 on/off 테스트
                        while True:
                            try:
                                number_input = input("Enter 0 or 1, 돌아가기: a: ")
                            except ValueError:
                                print("잘못된 입력입니다. 0 또는 1을 입력하세요.")
                                continue

                            if number_input == '1':   # 1 입력 시 LED ON
                                selected_pin.on() 
                                #print(f"GPIO {pin_number_input} - LED ON")
                                print(f"GPIO {selected_pin} - LED ON")
                            elif number_input == '0':
                                selected_pin.off() 
                                print(f"GPIO {pin_number_input} - led off")
                            elif number_input == 'a':
                                break
                            else:
                                print("잘못된 입력입니다. 0 또는 1을 입력하세요.")

            # 'e' 종료 
            if( c==14 ):            
                break

    # 예외처리
    except KeyboardInterrupt:
        print("프로그램 종료.")
    finally:
        try:
            # GPIO.setup(27, GPIO.OUT)    # GPIO 27번 전원 제어 제거 (입력 전용 사용)
            # GPIO.output(27, False)      # GPIO 27번 전원 제어 제거 (입력 전용 사용)
            pass
        except Exception:
            pass
        GPIO.cleanup()
        sys.exit()
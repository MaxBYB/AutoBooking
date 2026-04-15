from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from captcha_solver import get_ordered_click_points_with_image_size # 识别验证码并返回点击坐标
import time
import datetime
import warnings
import re
warnings.filterwarnings('ignore')


# def login(driver, user_name, password, retry=0):
#     if retry == 1:
#         return '智慧场馆登录失败\n'

#     print('智慧场馆登录中...')

#     driver.get('https://epe.pku.edu.cn/venue/login')

#     # epe新版会先停留在/venue/login，需要手动点“统一身份认证登录（IAAA）”
#     if 'epe.pku.edu.cn/venue/login' in driver.current_url.lower() and len(driver.find_elements(By.ID, 'user_name')) == 0:
#         iaaa_buttons = driver.find_elements(
#             By.XPATH, "//*[contains(normalize-space(text()), '统一身份认证登录') or contains(normalize-space(text()), 'IAAA')]")
#         if len(iaaa_buttons) > 0:
#             driver.execute_script('arguments[0].click();', iaaa_buttons[0])
#             time.sleep(10)

#     # 如果当前还没有进入IAAA表单页，兜底再尝试一次通用“登录”按钮
#     if len(driver.find_elements(By.ID, 'user_name')) == 0:
#         login_buttons = driver.find_elements(
#             By.XPATH, "//*[contains(normalize-space(text()), '登录')]")
#         if len(login_buttons) > 0:
#             driver.execute_script('arguments[0].click();', login_buttons[0])
#             time.sleep(10)

#     has_login_form = len(driver.find_elements(By.ID, 'user_name')) > 0 and len(
#         driver.find_elements(By.ID, 'password')) > 0 and len(driver.find_elements(By.ID, 'logon_button')) > 0
#     if has_login_form:
#         WebDriverWait(driver, 20).until(
#             EC.visibility_of_element_located((By.ID, 'logon_button')))
#         time.sleep(0.2)
#         user_input = driver.find_element(By.ID, 'user_name')
#         pwd_input = driver.find_element(By.ID, 'password')
#         user_input.clear()
#         pwd_input.clear()
#         user_input.send_keys(user_name)
#         time.sleep(0.2)
#         pwd_input.send_keys(password)
#         time.sleep(0.2)
#         driver.find_element(By.ID, 'logon_button').click()

#     try:
#         WebDriverWait(driver,
#                       25).until(lambda d: 'epe.pku.edu.cn/venue' in d.current_url.lower() and len(d.find_elements(By.ID, 'user_name')) == 0)
#         print('智慧场馆登录成功')
#         return '智慧场馆登录成功\n'
#     except Exception as e:
#         print('Retrying...', e)
#         return login(driver, user_name, password, retry + 1)


# def login(driver, user_name, password, retry=0):
#     if retry >= 3:
#         raise Exception("登录失败，重试次数已达上限")

#     print("打开智慧场馆登录页...")
#     driver.get("https://epe.pku.edu.cn/venue/login")

#     wait = WebDriverWait(driver, 15)

#     try:
#         # 1. 等待并点击“统一身份认证登录（IAAA）”按钮
#         iaaa_button = wait.until(
#             EC.element_to_be_clickable(
#                 (
#                     By.XPATH,
#                     "//button[contains(., '统一身份认证登录') or contains(., 'IAAA')]"
#                 )
#             )
#         )
#         iaaa_button.click()
#         print("已点击 IAAA 登录按钮")

#         # 2. 等待跳转到 IAAA 登录页
#         wait.until(lambda d: "iaaa" in d.current_url.lower() or "oauth" in d.current_url.lower())
#         print("已跳转到 IAAA 登录页:", driver.current_url)

#         # 3. 等待用户名和密码输入框出现
#         username_input = wait.until(
#             EC.presence_of_element_located((By.ID, "user_name"))
#         )
#         password_input = wait.until(
#             EC.presence_of_element_located((By.ID, "password"))
#         )

#         # 4. 输入账号密码
#         username_input.clear()
#         username_input.send_keys(user_name)
#         password_input.clear()
#         password_input.send_keys(password)

#         # 5. 点击登录按钮
#         login_button = wait.until(
#             EC.element_to_be_clickable((By.ID, "logon_button"))
#         )
#         login_button.click()
#         print("已提交 IAAA 登录表单")

#         # 6. 等待跳回智慧场馆系统
#         wait.until(lambda d: "epe.pku.edu.cn/venue" in d.current_url.lower())
#         print("已返回智慧场馆系统:", driver.current_url)

#         # 给前端一点加载时间
#         time.sleep(2)

#         return "登录成功\n"

#     except Exception as e:
#         print("登录异常：", repr(e))
#         if retry < 2:
#             print("准备重试...")
#             time.sleep(1)
#             return login(driver, user_name, password, retry + 1)
#         raise

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login(driver, user_name, password, retry=0):
    if retry >= 3:
        raise Exception("登录失败，重试次数已达上限")

    print("直接进入 IAAA 登录流程...")
    wait = WebDriverWait(driver, 20)

    try:
        # 关键修改：直接访问 SSO 入口
        driver.get("https://epe.pku.edu.cn/venue-server/loginto")

        print("当前URL:", driver.current_url)

        # 等待跳转到 IAAA（不同学校可能是 iaaa / oauth / auth）
        wait.until(
            lambda d: any(x in d.current_url.lower() for x in ["iaaa", "oauth", "auth"])
        )

        print("已跳转到登录页:", driver.current_url)

        # 等待输入框加载
        username_input = wait.until(
            EC.presence_of_element_located((By.ID, "user_name"))
        )
        password_input = wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        # 输入账号密码
        username_input.clear()
        username_input.send_keys(user_name)

        password_input.clear()
        password_input.send_keys(password)

        # 点击登录
        login_button = wait.until(
            EC.element_to_be_clickable((By.ID, "logon_button"))
        )
        login_button.click()

        print("已提交登录信息，等待跳转...")

        # 等待跳回智慧场馆系统
        wait.until(
            lambda d: "epe.pku.edu.cn/venue" in d.current_url.lower()
        )

        print("登录成功，当前URL:", driver.current_url)

        time.sleep(2)
        return "登录成功\n"

    except Exception as e:
        print("登录异常：", repr(e))

        # 保存调试页面
        with open("debug_login_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("已保存当前页面源码到 debug_login_page.html")

        if retry < 2:
            print("准备重试...")
            time.sleep(2)
            return login(driver, user_name, password, retry + 1)

        raise

def go_to_venue(driver, venue, retry=0):
    if retry == 1:
        print("进入预约 %s 界面失败" % venue)
        log_str = "进入预约 %s 界面失败\n" % venue
        return False, log_str

    print("进入预约 %s 界面" % venue)
    log_str = "进入预约 %s 界面\n" % venue

    try:
        driver.get('https://epe.pku.edu.cn/venue/home')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(normalize-space(text()), '%s')]" % venue)))
        driver.find_element(By.XPATH, "//*[contains(normalize-space(text()), '%s')]" % venue).click()
        status = True
        log_str += "进入预约 %s 界面成功\n" % venue
    except Exception as e:
        print("retrying", e)
        print("当前URL:", driver.current_url)
        log_str += "进入预约异常: %s\n" % str(e)
        log_str += "当前URL: %s\n" % driver.current_url
        status, log_str = go_to_venue(driver, venue, retry + 1)
    return status, log_str


def click_agree(driver):
    print("点击同意")
    log_str = "点击同意\n"
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'ivu-checkbox-wrapper')))
    time.sleep(0.1)
    driver.find_element(By.CLASS_NAME, 'ivu-checkbox-wrapper').click()
    print("点击同意成功\n")
    log_str += "点击同意成功\n"
    return log_str


def judge_exceeds_days_limit(start_time, end_time):
    start_time_list = start_time.split('/')
    end_time_list = end_time.split('/')
    print(start_time_list, end_time_list)
    now = datetime.datetime.today()
    today = datetime.datetime.strptime(str(now)[:10], "%Y-%m-%d")
    time_hour = datetime.datetime.strptime(
        str(now).split()[1][:-7], "%H:%M:%S")
    time_11_55 = datetime.datetime.strptime(
        "11:55:00", "%H:%M:%S")
    # time_11_55 = datetime.datetime.strptime(
    #     str(now).split()[1][:-7], "%H:%M:%S")

    start_time_list_new = []
    end_time_list_new = []
    delta_day_list = []

    for k in range(len(start_time_list)):
        start_time = start_time_list[k]
        end_time = end_time_list[k]
        if len(start_time) > 8:
            date = datetime.datetime.strptime(
                start_time.split('-')[0], "%Y%m%d")
            delta_day = (date-today).days
        else:
            delta_day = (int(start_time[0])+6-today.weekday()) % 7
            date = today+datetime.timedelta(days=delta_day)
        print("日期:", str(date).split()[0])
        # print(delta_day)
        if delta_day > 3 or (delta_day == 3 and (time_hour < time_11_55)):
            print("只能在当天中午11:55后预约未来3天以内的场馆")
            log_str = "只能在当天中午11:55后预约未来3天以内的场馆\n"
            break
        else:
            start_time_list_new.append(start_time)
            end_time_list_new.append(end_time)
            delta_day_list.append(delta_day)
            print("在预约可预约日期范围内")
            log_str = "在预约可预约日期范围内\n"
    return start_time_list_new, end_time_list_new, delta_day_list, log_str


# def book(driver, start_time_list, end_time_list, delta_day_list, venue_num=-1):
#     print("查找空闲场地")
#     log_str = "查找空闲场地\n"

#     def judge_close_to_time_12():
#         now = datetime.datetime.today()
#         time_hour = datetime.datetime.strptime(
#             str(now).split()[1][:-7], "%H:%M:%S")
#         time_11_55 = datetime.datetime.strptime(
#             "11:55:00", "%H:%M:%S")
#         time_12 = datetime.datetime.strptime(
#             "12:00:00", "%H:%M:%S")
#         # time_11_55 = datetime.datetime.strptime(
#         #     str(now).split()[1][:-7], "%H:%M:%S")
#         # time_12 = time_11_55+datetime.timedelta(minutes=1)
#         if time_hour < time_11_55:
#             return 0
#         elif time_11_55 < time_hour < time_12:
#             return 1
#         elif time_hour > time_12:
#             return 2

#     def judge_in_time_range(start_time, end_time, venue_time_range):
#         vt = venue_time_range.split('-')
#         vt_start_time = datetime.datetime.strptime(vt[0], "%H:%M")
#         vt_end_time = datetime.datetime.strptime(vt[1], "%H:%M")
#         if start_time <= vt_start_time and vt_end_time <= end_time:
#             return True
#         else:
#             return False

#     def move_to_date(delta_day):
#         for i in range(delta_day):
#             WebDriverWait(driver, 10).until_not(
#                 EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
#             driver.find_element(By.XPATH,
#                 '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/form/div/div/button[2]/i').click()
#             time.sleep(0.2)

#     def click_free(start_time, end_time, venue_num, table_num):
#         trs = driver.find_elements(By.TAG_NAME, 'tr')
#         # 防止表格没加载出来
#         no_table_flag = 0
#         while trs[1].find_elements(By.TAG_NAME,
#                 'td')[0].find_element(By.TAG_NAME, 'div').text == "时间段":
#             no_table_flag += 1
#             time.sleep(0.2)
#             trs = driver.find_elements(By.TAG_NAME, 'tr')
#             if no_table_flag > 10:
#                 driver.refresh()
#                 no_table_flag = 0
#                 move_to_date(delta_day)
#         trs_list = []
#         for i in range(1, len(trs)-2):
#             vt = trs[i].find_elements(By.TAG_NAME,
#                 'td')[0].find_element(By.TAG_NAME, 'div').text
#             if judge_in_time_range(start_time, end_time, vt):
#                 trs_list.append(trs[i].find_elements(By.TAG_NAME,
#                     'td'))
#         if len(trs_list) == 0:
#             return False, -1, 0

#         j_list = [x for x in range(1, len(trs_list[0]))]
#         print(venue_num, table_num, j_list)
#         if venue_num != -1 and (venue_num-table_num in j_list):
#             flag = False
#             for i in range(len(trs_list)):
#                 class_name = trs_list[i][venue_num-table_num].find_element(By.TAG_NAME,
#                     'div').get_attribute("class")
#                 print(class_name)
#                 if class_name.split()[2] == 'free':
#                     flag = True
#                     break
#         elif venue_num != -1 and (venue_num-table_num not in j_list):
#             return False, venue_num, table_num + len(j_list)
#         else:
#             # 随机点一列free的，防止每次都点第一列
#             random.shuffle(j_list)
#             print(j_list)
#             for j in j_list:
#                 flag = False
#                 for i in range(len(trs_list)):
#                     class_name = trs_list[i][j].find_element(By.TAG_NAME,
#                         'div').get_attribute("class")
#                     print(class_name)
#                     if class_name.split()[2] == 'free':
#                         flag = True
#                         venue_num = j+table_num
#                         break
#         if flag:
#             for i in range(len(trs_list)):
#                 WebDriverWait(driver, 10).until_not(
#                     EC.visibility_of_element_located((By.CSS_SELECTOR,
#                                                       ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix.fade-leave-active.fade-leave-to")))
#                 trs_list[i][venue_num-table_num].find_element(By.TAG_NAME,
#                     'div').click()
#             return True, venue_num, table_num + len(j_list)
#         return False, venue_num, table_num + len(j_list)

#     driver.switch_to.window(driver.window_handles[-1])
#     time.sleep(1)
#     WebDriverWait(driver, 10).until_not(
#         EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
#     try:
#         WebDriverWait(driver, 8).until(
#             EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/form/div/div/div/div[1]/div/div/input')))
#     except Exception:
#         # 兼容新版页面结构：不再依赖旧的绝对XPath，等待预约表格核心元素出现
#         WebDriverWait(driver, 15).until(
#             lambda d: len(d.find_elements(By.TAG_NAME, 'tr')) > 1 or len(
#                 d.find_elements(By.XPATH, "//*[contains(normalize-space(text()), '时间段')]")
#             ) > 0)
#     # 若接近但是没到12点，停留在此页面
#     flag = judge_close_to_time_12()
#     if flag == 1:
#         while True:
#             flag = judge_close_to_time_12()
#             if flag == 2:
#                 break
#             else:
#                 time.sleep(0.5)
#         driver.refresh()
#         WebDriverWait(driver, 5).until_not(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))

#     for k in range(len(start_time_list)):
#         start_time = start_time_list[k]
#         end_time = end_time_list[k]
#         delta_day = delta_day_list[k]

#         if k != 0:
#             driver.refresh()
#             time.sleep(0.5)

#         move_to_date(delta_day)

#         start_time = datetime.datetime.strptime(
#             start_time.split('-')[1], "%H%M")
#         end_time = datetime.datetime.strptime(end_time.split('-')[1], "%H%M")
#         print("开始时间:%s" % str(start_time).split()[1])
#         print("结束时间:%s" % str(end_time).split()[1])

#         status, venue_num, table_num = click_free(
#             start_time, end_time, venue_num, 0)
#         # 如果第一页没有，就往后翻，直到不存在下一页
#         while not status:
#             next_table = driver.find_elements(By.XPATH,
#                 '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/thead/tr/td[6]/div/span/i')
#             WebDriverWait(driver, 10).until_not(
#                 EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
#             time.sleep(0.1)
#             if len(next_table) > 0:
#                 driver.find_element(By.XPATH,
#                     '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/table/thead/tr/td[6]/div/span/i').click()
#                 status, venue_num, table_num = click_free(
#                     start_time, end_time, venue_num, table_num)
#             else:
#                 break
#         if status:
#             log_str += "找到空闲场地，场地编号为%d\n" % venue_num
#             print("找到空闲场地，场地编号为%d\n" % venue_num)
#             now = datetime.datetime.now()
#             today = datetime.datetime.strptime(str(now)[:10], "%Y-%m-%d")
#             date = today+datetime.timedelta(days=delta_day)
#             return status, log_str, str(date)[:10]+str(start_time)[10:], str(date)[:10]+str(end_time)[10:], venue_num
#         else:
#             log_str += "没有空余场地\n"
#             print("没有空余场地\n")
#     return status, log_str, None, None, None

def book(driver, start_time_list, end_time_list, delta_day_list, venue_num=-1):
    print("查找空闲场地")
    log_str = "查找空闲场地\n"

    def judge_close_to_time_12():
        now = datetime.datetime.today()
        time_hour = datetime.datetime.strptime(
            str(now).split()[1][:-7], "%H:%M:%S")
        time_11_55 = datetime.datetime.strptime("11:55:00", "%H:%M:%S")
        time_12 = datetime.datetime.strptime("12:00:00", "%H:%M:%S")
        if time_hour < time_11_55:
            return 0
        elif time_11_55 < time_hour < time_12:
            return 1
        else:
            return 2

    def normalize_text(s):
        return (s or "").strip().replace(" ", "").replace("\n", "").replace("\t", "")

    # def move_to_date(delta_day):
    #     """
    #     新版页面顶部日期块切换：
    #     当前页通常会显示未来几天的日期卡片。
    #     这里优先通过日期文本点击目标日期，而不是沿用旧版绝对 XPath。
    #     """
    #     target_date = (datetime.datetime.today() + datetime.timedelta(days=delta_day)).strftime("%m月%d日")
    #     print("目标日期文本:", target_date)

    #     # 等日期区域渲染出来
    #     WebDriverWait(driver, 15).until(
    #         lambda d: len(d.find_elements(By.XPATH, f"//*[contains(text(), '{target_date}')]")) > 0
    #     )

    #     candidates = driver.find_elements(By.XPATH, f"//*[contains(text(), '{target_date}')]")
    #     clicked = False
    #     for el in candidates:
    #         try:
    #             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    #             time.sleep(0.2)
    #             driver.execute_script("arguments[0].click();", el)
    #             clicked = True
    #             print("已点击日期:", target_date)
    #             time.sleep(0.5)
    #             break
    #         except Exception:
    #             continue

    #     if not clicked:
    #         raise Exception(f"未能点击目标日期 {target_date}")

    def move_to_date(delta_day):
        target_date = (datetime.datetime.today() + datetime.timedelta(days=delta_day)).strftime("%m月%d日")
        print("目标日期文本:", target_date)

        # 等待日期区域出现
        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(By.XPATH, f"//span[normalize-space()='{target_date}']")) > 0
        )

        # 先找到日期文字所在的 span
        date_span = driver.find_element(By.XPATH, f"//span[normalize-space()='{target_date}']")

        # 再找到可点击的日期卡片容器
        # 从 span 往上找最近的“日期块” div
        clickable_box = date_span.find_element(
            By.XPATH,
            "./ancestor::div[contains(@style,'order')][1]"
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_box)
        time.sleep(0.2)

        # 优先用 JS 点击，避免被内层遮挡
        driver.execute_script("arguments[0].click();", clickable_box)
        print("已点击日期卡片:", target_date)

        time.sleep(0.8)


    # def get_target_col_index(target_slot_text):
    #     """
    #     从表头找到目标时间段所在列。
    #     表头第一列是“场地”，后面各列是时间段。
    #     返回实际 td 索引。
    #     """
    #     header_tds = driver.find_elements(By.CSS_SELECTOR, "table thead tr td")
    #     if len(header_tds) == 0:
    #         raise Exception("未找到表头列")

    #     for idx, td in enumerate(header_tds):
    #         text = normalize_text(td.text)
    #         if target_slot_text in text:
    #             print("找到目标时间列:", text, "索引:", idx)
    #             return idx

    #     return None

    def get_target_col_index(target_slot_text):
        """
        只从当前可见主表读取时间表头
        只收集真正的时间列表头，例如 06:50-07:50
        返回的是“时间列序号”，不是全 td 序号
        """
        time_headers = []
        tables = driver.find_elements(By.CSS_SELECTOR, "table")

        for table_el in tables:
            try:
                if not table_el.is_displayed():
                    continue

                headers = []
                tds = table_el.find_elements(By.CSS_SELECTOR, "thead tr td")
                for td in tds:
                    text = normalize_text(td.text)
                    if re.fullmatch(r"\d{2}:\d{2}-\d{2}:\d{2}", text):
                        headers.append(text)

                if headers:
                    time_headers = headers
                    break
            except Exception:
                continue

        print("检测到的时间表头:", time_headers)

        for idx, text in enumerate(time_headers):
            if text == target_slot_text:
                print("找到目标时间列:", text, "时间列序号:", idx)
                return idx

        return None


    def is_available_cell(td):
        """
        判定单元格是否可订：
        1. reserveBlock 的 class 含 free -> 可订
        2. class 含 reserved 或 title/text 为已售 -> 不可订
        3. 文本含 ￥ / ¥ 作为兜底可订
        """
        try:
            block = td.find_element(By.CSS_SELECTOR, "div.reserveBlock")
        except Exception:
            return False

        class_name = (block.get_attribute("class") or "").strip()
        classes = class_name.split()
        text = normalize_text(block.text)

        title = ""
        try:
            p = block.find_element(By.TAG_NAME, "p")
            title = normalize_text(p.get_attribute("title"))
        except Exception:
            pass

        print("单元格 class:", class_name, "text:", text, "title:", title)

        if "reserved" in classes:
            return False
        if "已售" in text or "已售" in title:
            return False
        if "free" in classes:
            return True
        if "￥" in text or "¥" in text or "￥" in title or "¥" in title:
            return True

        return False

    def click_target_cell(td):
        """
        点击 reserveBlock 本体，而不是旧版里的内层 div
        """
        block = td.find_element(By.CSS_SELECTOR, "div.reserveBlock")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", block)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", block)
        time.sleep(0.3)

    def get_row_venue_num(row):
        """
        每行第一列是场地号，例如“1号”
        """
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) == 0:
            return None
        venue_text = normalize_text(tds[0].text)
        try:
            return int(venue_text.replace("号", ""))
        except Exception:
            return None

    def try_find_and_click_slot(target_slot_text, wanted_venue_num):
        """
        在当前页里查找目标时间列，并在所有场地行里点击可订单元格。
        如果指定 wanted_venue_num，则只尝试该场地。
        """
        target_col_idx = get_target_col_index(target_slot_text)
        if target_col_idx is None:
            print("当前页没有目标时间列:", target_slot_text)
            return False, -1

        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print("当前表格行数:", len(rows))

        for row in rows:
            row_venue_num = get_row_venue_num(row)
            if row_venue_num is None:
                continue

            if wanted_venue_num != -1 and row_venue_num != wanted_venue_num:
                continue

            tds = row.find_elements(By.TAG_NAME, "td")

            # 第 0 列是场地号，所以时间列要 +1
            actual_td_idx = target_col_idx + 1
            if len(tds) <= actual_td_idx:
                continue

            target_td = tds[actual_td_idx]
            print(f"检查场地 {row_venue_num} 号，目标列索引 {target_col_idx}")

            if is_available_cell(target_td):
                try:
                    click_target_cell(target_td)
                    print(f"成功点击场地 {row_venue_num} 号，时间段 {target_slot_text}")
                    return True, row_venue_num
                except Exception as e:
                    print("点击单元格失败:", e)

        return False, -1

    # def goto_time_page_until_found(target_slot_text, wanted_venue_num, max_turns=12):
    #     """
    #     时间列可能分页显示，右上角有箭头。
    #     这里逐页查找目标时间列。
    #     """
    #     for _ in range(max_turns):
    #         status, found_venue_num = try_find_and_click_slot(target_slot_text, wanted_venue_num)
    #         if status:
    #             return True, found_venue_num

    #         # 尝试点击右箭头翻时间页
    #         next_candidates = driver.find_elements(
    #             By.XPATH,
    #             "//*[contains(@class,'arrowWrap') or contains(@class,'arrow')]"
    #         )

    #         clicked = False
    #         for btn in next_candidates:
    #             try:
    #                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    #                 time.sleep(0.1)
    #                 driver.execute_script("arguments[0].click();", btn)
    #                 print("点击时间翻页箭头")
    #                 time.sleep(0.5)
    #                 clicked = True
    #                 break
    #             except Exception:
    #                 continue

    #         if not clicked:
    #             print("未找到可用的时间翻页箭头")
    #             break

    #     return False, -1

    def goto_time_page_until_found(target_slot_text, wanted_venue_num, max_turns=12):
        """
        时间列可能分页显示。
        只点击“当前主预约表表头最后一个时间列”里的右箭头。
        """

        def get_visible_time_headers():
            tables = driver.find_elements(By.CSS_SELECTOR, "table")
            for table in tables:
                try:
                    if not table.is_displayed():
                        continue

                    tds = table.find_elements(By.CSS_SELECTOR, "thead tr td")
                    headers = []
                    for td in tds:
                        text = normalize_text(td.text)
                        if re.fullmatch(r"\d{2}:\d{2}-\d{2}:\d{2}", text):
                            headers.append(text)

                    # 只接受真正的预约表：既有时间头，也有 reserveBlock
                    if headers and len(table.find_elements(By.CSS_SELECTOR, "div.reserveBlock")) > 0:
                        return headers
                except Exception:
                    continue
            return []

        def find_right_arrow_for_current_table():
            """
            精确找到当前主预约表“最后一个时间列”里的右箭头 icon
            """
            current_headers = get_visible_time_headers()
            if not current_headers:
                return None, None

            last_header = current_headers[-1]
            print("当前最后一个时间表头:", last_header)

            tables = driver.find_elements(By.CSS_SELECTOR, "table")
            for table in tables:
                try:
                    if not table.is_displayed():
                        continue

                    if len(table.find_elements(By.CSS_SELECTOR, "div.reserveBlock")) == 0:
                        continue

                    header_tds = table.find_elements(By.CSS_SELECTOR, "thead tr td")
                    for td in header_tds:
                        text = normalize_text(td.text)

                        # 找到“最后一个时间段”对应的表头单元格
                        if last_header == text:
                            icons = td.find_elements(By.CSS_SELECTOR, "i.ivu-icon.ivu-icon-ios-arrow-forward")
                            for icon in icons:
                                if icon.is_displayed():
                                    return icon, table
                except Exception:
                    continue

            return None, None

        def click_right_arrow_and_wait_change():
            before_headers = get_visible_time_headers()
            print("点击前时间表头:", before_headers)

            icon, table = find_right_arrow_for_current_table()
            if icon is None:
                print("没有找到当前主预约表最后一个时间列里的右箭头")
                return False

            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
                time.sleep(0.1)

                # 先尝试原生 click
                try:
                    icon.click()
                    print("已原生点击正确表头中的右箭头 icon")
                except Exception:
                    driver.execute_script("arguments[0].click();", icon)
                    print("已JS点击正确表头中的右箭头 icon")
            except Exception as e:
                print("点击右箭头失败:", e)
                return False

            # 等待重新渲染后再抓
            time.sleep(1.0)

            try:
                WebDriverWait(driver, 5).until(
                    lambda d: (
                        len(get_visible_time_headers()) > 0 and
                        (
                            get_visible_time_headers() != before_headers or
                            target_slot_text in get_visible_time_headers()
                        )
                    )
                )
            except Exception:
                pass

            after_headers = get_visible_time_headers()
            print("点击后重新抓取时间表头:", after_headers)

            if target_slot_text in after_headers:
                print("翻页成功，目标时间已出现")
                return True

            if after_headers and after_headers != before_headers:
                print("翻页成功，表头已变化")
                return True

            print("翻页后表头未有效变化")
            return False

        for _ in range(max_turns):
            status, found_venue_num = try_find_and_click_slot(target_slot_text, wanted_venue_num)
            if status:
                return True, found_venue_num

            print("当前页没有目标时间列:", target_slot_text)
            turned = click_right_arrow_and_wait_change()
            if not turned:
                break

        return False, -1

    # 新版页面通常是单窗口，但保留兼容
    try:
        driver.switch_to.window(driver.window_handles[-1])
    except Exception:
        pass

    time.sleep(1)

    # 等待页面主体和表格加载
    WebDriverWait(driver, 15).until(
        lambda d: len(d.find_elements(By.TAG_NAME, "table")) > 0
    )
    WebDriverWait(driver, 15).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "table thead tr td")) > 1
    )

    # 若接近但没到 12:00，停留等待
    flag = judge_close_to_time_12()
    if flag == 1:
        print("接近 12 点，等待开抢...")
        while True:
            flag = judge_close_to_time_12()
            if flag == 2:
                break
            time.sleep(0.5)
        driver.refresh()
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "table")) > 0
        )
        time.sleep(1)

    for k in range(len(start_time_list)):
        raw_start_time = start_time_list[k]
        raw_end_time = end_time_list[k]
        delta_day = delta_day_list[k]

        if k != 0:
            driver.refresh()
            time.sleep(1)

        # 切换到目标日期
        move_to_date(delta_day)

        # 配置格式例如：20260416-0650 / 20260416-0750
        start_dt = datetime.datetime.strptime(raw_start_time.split('-')[1], "%H%M")
        end_dt = datetime.datetime.strptime(raw_end_time.split('-')[1], "%H%M")
        target_slot_text = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"

        print("目标开始时间:", start_dt.strftime('%H:%M'))
        print("目标结束时间:", end_dt.strftime('%H:%M'))
        print("目标时间段文本:", target_slot_text)

        status, found_venue_num = goto_time_page_until_found(target_slot_text, venue_num)

        if status:
            log_str += f"找到空闲场地，场地编号为{found_venue_num}\n"
            print(f"找到空闲场地，场地编号为{found_venue_num}\n")

            now = datetime.datetime.now()
            today = datetime.datetime.strptime(str(now)[:10], "%Y-%m-%d")
            date = today + datetime.timedelta(days=delta_day)

            return (
                True,
                log_str,
                str(date)[:10] + " " + start_dt.strftime('%H:%M:%S'),
                str(date)[:10] + " " + end_dt.strftime('%H:%M:%S'),
                found_venue_num
            )
        else:
            log_str += f"没有找到时间段 {target_slot_text} 的空余场地\n"
            print(f"没有找到时间段 {target_slot_text} 的空余场地\n")

    return False, log_str, None, None, None

# def click_book(driver):
#     print("确定预约")
#     log_str = "确定预约\n"
#     driver.switch_to.window(driver.window_handles[-1])
#     WebDriverWait(driver, 10).until_not(
#         EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
#     WebDriverWait(driver, 10).until(
#         EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[5]/div/div[2]')))
#     driver.find_element(By.XPATH,
#         '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[5]/div/div[2]').click()
#     print("确定预约成功")
#     log_str += "确定预约成功\n"
#     return log_str

def click_book(driver):
    print("确定预约")
    log_str = "确定预约\n"

    try:
        # 新版页面通常不需要切窗口，但保留兼容
        try:
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        # 等待提交区域出现
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.submit_order_box div.action div.btn")) > 0
        )

        # 优先按文本找“提交”
        submit_buttons = driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'submit_order_box')]//div[contains(@class,'btn') and normalize-space(text())='提交']"
        )

        clicked = False
        for btn in submit_buttons:
            try:
                if not btn.is_displayed():
                    continue
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", btn)
                clicked = True
                print("确定预约成功")
                log_str += "确定预约成功\n"
                break
            except Exception:
                continue

        if not clicked:
            raise Exception("未找到可点击的“提交”按钮")

        time.sleep(0.5)
        return log_str

    except Exception as e:
        print("确定预约失败:", e)
        raise


def click_submit_order(driver):
    print("提交订单")
    log_str = "提交订单\n"

    def extract_verify_targets(msg_text):
        # 示例: 请依次点击【并,果,界】
        text = (msg_text or "").strip()
        match = re.search(r"[【\[\(（](.*?)[】\]\)）]", text)
        content = match.group(1) if match else text
        items = [x.strip() for x in re.split(r"[，,、\s]+", content) if x.strip()]
        if not items:
            items = [ch for ch in content if ch.strip()]
        return items

    try:
        driver.switch_to.window(driver.window_handles[-1])
    except Exception:
        pass

    def has_visible_verifybox():
        boxes = driver.find_elements(By.CSS_SELECTOR, "div.verifybox")
        for b in boxes:
            try:
                if b.is_displayed():
                    return True
            except Exception:
                continue
        return False

    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))

    # 先点击“提交订单”按钮（兼容旧版XPath和新版文本按钮）
    clicked = False

    # 旧版按钮先做“快速尝试”，避免每次都等待较长超时
    try:
        legacy_buttons = driver.find_elements(
            By.XPATH,
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div[2]'
        )
        if legacy_buttons:
            driver.execute_script("arguments[0].click();", legacy_buttons[0])
            clicked = True
    except Exception:
        pass

    if not clicked:
        # 新版按钮短等待，兼顾稳定性和速度
        try:
            WebDriverWait(driver, 0.5).until(
                lambda d: len(
                    d.find_elements(
                        By.XPATH,
                        "//*[contains(@class,'btn') and (normalize-space(text())='提交订单' or normalize-space(text())='提交' or normalize-space(text())='确认提交')]"
                    )
                ) > 0
            )
        except Exception:
            pass

        submit_buttons = driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'btn') and normalize-space(text())='提交']"
        )
        for btn in submit_buttons:
            try:
                if not btn.is_displayed():
                    continue
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.1)
                driver.execute_script("arguments[0].click();", btn)
                clicked = True
                break
            except Exception:
                continue

    if not clicked:
        raise Exception("未找到提交订单按钮")

    # 0) 处理“请依次点击【】”图形验证码弹窗
    verify_boxes = driver.find_elements(By.CSS_SELECTOR, "div.verifybox")
    if verify_boxes:
        print("检测到图形验证码弹窗，开始识别并点击...")

        def find_visible_verify_img_element():
            verify_img_selectors = [
                "div.verifybox div.verify-img-area",
                "div.verifybox div.verify-img",
                "div.verifybox canvas",
                "div.verifybox img",
            ]
            for selector in verify_img_selectors:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elems:
                    if elem.is_displayed():
                        return elem
            return None

        def click_refresh_verify_image():
            refresh_selectors = [
                "div.verifybox div.verify-refresh",
                "div.verifybox i.icon-refresh",
                "div.verifybox i.iconfont.icon-refresh",
            ]
            for selector in refresh_selectors:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elems:
                    try:
                        if not elem.is_displayed():
                            continue
                        driver.execute_script("arguments[0].click();", elem)
                        return True
                    except Exception:
                        continue
            return False

        solved = False
        max_verify_retry = 4

        for attempt in range(1, max_verify_retry + 1):
            try:
                verify_msg_el = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "span.verify-msg"))
                )
                verify_text = verify_msg_el.text.strip()
                targets = extract_verify_targets(verify_text)
                print(f"验证码第{attempt}次，目标顺序: {targets}")

                verify_img_el = find_visible_verify_img_element()
                if verify_img_el is None:
                    raise Exception("未找到验证码图片容器元素")

                t0 = time.perf_counter()
                img_bytes = verify_img_el.screenshot_as_png
                t1 = time.perf_counter()

                try:
                    points, img_w, img_h = get_ordered_click_points_with_image_size(
                        img_bytes,
                        targets,
                        fast_mode=True,
                    )
                    mode = "fast"
                except Exception:
                    points, img_w, img_h = get_ordered_click_points_with_image_size(
                        img_bytes,
                        targets,
                        fast_mode=False,
                    )
                    mode = "fallback"
                t2 = time.perf_counter()

                print(
                    "验证码耗时: screenshot=%.3fs, ocr(%s)=%.3fs"
                    % (t1 - t0, mode, t2 - t1)
                )
                print("识别到点击坐标:", points)

                for x, y in points:
                    # 在验证码元素内部按相对坐标点击，避免 ActionChains 偏移差异
                    rx = float(x) / float(img_w)
                    ry = float(y) / float(img_h)
                    driver.execute_script(
                        """
                        const el = arguments[0];
                        const rx = arguments[1];
                        const ry = arguments[2];
                        const rect = el.getBoundingClientRect();
                        const ox = rx * rect.width;
                        const oy = ry * rect.height;
                        const clientX = rect.left + ox;
                        const clientY = rect.top + oy;
                        const evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX,
                            clientY
                        });
                        el.dispatchEvent(evt);
                        """,
                        verify_img_el,
                        rx,
                        ry,
                    )
                    time.sleep(0.25)

                # 等待验证码框关闭，若未关闭则刷新重试
                try:
                    WebDriverWait(driver, 4).until(
                        lambda d: not has_visible_verifybox()
                    )
                    solved = True
                    log_str += "已完成图形验证码点击\n"
                    break
                except Exception:
                    # 有时已通过但 DOM 仍在变更，这里再做一次状态确认
                    if not has_visible_verifybox():
                        solved = True
                        log_str += "已完成图形验证码点击\n"
                        break
                    print(f"第{attempt}次验证码可能未通过，尝试刷新验证码")
                    if attempt < max_verify_retry:
                        refreshed = click_refresh_verify_image()
                        if not refreshed:
                            print("未找到验证码刷新按钮，稍后重试")
                        time.sleep(0.6)
                    else:
                        break

            except Exception as e:
                print(f"第{attempt}次验证码处理异常: {e}")

                # 若异常发生时验证码弹窗已消失，视为本轮已通过
                if not has_visible_verifybox():
                    solved = True
                    log_str += "已完成图形验证码点击\n"
                    break

                if attempt < max_verify_retry:
                    refreshed = click_refresh_verify_image()
                    if refreshed:
                        print("已点击刷新验证码，准备重试")
                    time.sleep(0.6)
                else:
                    break

        if not solved:
            raise Exception("验证码多次识别/点击后仍未通过")

    # 1) 捕捉原生 alert 弹窗
    try:
        alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert_text = alert.text
        print("捕捉到原生弹窗:", alert_text)
        log_str += "弹窗内容: %s\n" % alert_text
        alert.accept()
        log_str += "已确认原生弹窗\n"
    except Exception:
        pass

    # 2) 捕捉页面内模态弹窗（如 ivu-modal）
    modal_buttons = driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'ivu-modal')]//*[contains(@class,'btn') and (normalize-space(text())='确定' or normalize-space(text())='确认' or normalize-space(text())='我知道了' or normalize-space(text())='继续提交')]"
    )
    for btn in modal_buttons:
        try:
            if not btn.is_displayed():
                continue
            driver.execute_script("arguments[0].click();", btn)
            log_str += "已确认页面弹窗\n"
            break
        except Exception:
            continue

    print("提交订单成功")
    log_str += "提交订单成功\n"
    return log_str


def click_pay(driver):
    print("付款（校园卡）")
    log_str = "付款（校园卡）\n"
    try:
        driver.switch_to.window(driver.window_handles[-1])
    except Exception:
        pass

    WebDriverWait(driver, 12).until_not(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix"))
    )

    # 新版页面默认已选校园卡，只需点击底部按钮组里的“支付”按钮。
    # 该按钮常见结构: div.btn-group > div.btn("支付") + span("(576s)")
    specific_pay_selectors = [
        (By.XPATH, "//div[contains(@class,'btn-group')]//div[contains(@class,'btn') and contains(normalize-space(.), '支付') and not(contains(normalize-space(.), '取消'))]"),
        (By.XPATH, "//div[contains(@class,'btn-group')]//*[contains(@class,'btn') and .//span[contains(normalize-space(.), 's')] and contains(normalize-space(.), '支付')]"),
    ]

    pay_selectors = [
        (By.XPATH, "//button[normalize-space(text())='支付' or normalize-space(text())='立即支付' or normalize-space(text())='确认支付']"),
        (By.XPATH, "//div[contains(@class,'btn') and (normalize-space(text())='支付' or normalize-space(text())='立即支付' or normalize-space(text())='确认支付') ]"),
        (By.XPATH, "//*[contains(@class,'pay') and (self::button or self::div or self::span)]"),
    ]

    clicked = False
    for by, selector in specific_pay_selectors + pay_selectors:
        elements = driver.find_elements(by, selector)
        for el in elements:
            try:
                if not el.is_displayed():
                    continue
                text = (el.text or "").strip()
                if "取消" in text:
                    continue
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                time.sleep(0.2)
                try:
                    el.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", el)
                clicked = True
                break
            except Exception:
                continue
        if clicked:
            break

    if not clicked:
        raise Exception("未找到可点击的支付按钮")

    # 点击后等待页面状态变化，避免误判。
    time.sleep(0.5)
    try:
        WebDriverWait(driver, 8).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".loading.ivu-spin.ivu-spin-large.ivu-spin-fix"))
        )
    except Exception:
        pass

    print("付款成功")
    log_str += "付款成功\n"
    return log_str


if __name__ == '__main__':
    pass

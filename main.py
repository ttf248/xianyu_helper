from xianyu import xianyu





        # # 计算关卡位置
        # (x1, y1) = win32gui.ClientToScreen(hwnd, (204, 182))
        # (x2, y2) = win32gui.ClientToScreen(hwnd, (398, 224))

        # game_level = 0
        # time_start = datetime.now()

        # img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        # result = reader.readtext(cv2.cvtColor(
        #     nm.array(img), cv2.COLOR_BGR2GRAY))
        # if len(result) > 0:
        #     game_level = result[0][1]
        #     logger.info("启动脚本，检测当前关卡：{}", game_level)

        # loop_count = 0
        # while True:
        #     loop_count = loop_count + 1
        #     if loop_count % 1000 == 0:
        #         img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        #         result = reader.readtext(cv2.cvtColor(
        #             nm.array(img), cv2.COLOR_BGR2GRAY))
        #         if len(result) > 0 and result[0][1] != game_level:
        #             game_level = result[0][1]
        #             time_consume = (datetime.now() - time_start)
        #             time_start = datetime.now()
        #             logger.info("检测到关卡变动：{}, 耗时：{}", game_level, time_consume)

        #     left_click_position(hwnd, 299, 783, 0.01)

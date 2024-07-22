"""
发送飞书通知
"""
import json
import logging
import time
import datetime
import requests
import urllib3
from utils.other_tools.allure_data.allure_report_data import TestMetrics
from utils import config


urllib3.disable_warnings()

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
  非空字符串
  :param content: 字符串
  :return: 非空 - True，空 - False
  """
    return bool(content and content.strip())


class FeiShuTalkChatBot:
    """飞书机器人通知"""
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics

    def send_text(self, msg: str):
        """
    消息类型为text类型
    :param msg: 消息内容
    :return: 返回消息发送结果
    """
        data = {"msg_type": "text", "at": {}}
        if is_not_null_and_blank_str(msg):  # 传入msg非空
            data["content"] = {"text": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        logging.debug('text类型：%s', data)
        return self.post()

    def post(self):
        """
    发送消息（内容UTF-8编码）
    :return: 返回消息发送结果
    """
        is_all_testcase_passed = self.metrics.total == self.metrics.passed
        header_color = "blue" if is_all_testcase_passed else "red"
        header_text = "🎉 自动化测试通过~" if is_all_testcase_passed else "😱 有失败的用例！"
        rich_text = {
            "msg_type": "interactive",
            "card": {
              "elements": [
                {
                  "tag": "markdown",
                  "content": "**🤖 测试人员： " + f"{config.tester_name}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**🚀 运行环境： " + f"{config.env}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**💌 成功率： " + f"{self.metrics.pass_rate} %" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**🎖️ 用例数： " + f"{self.metrics.total}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**⭕ 成功用例： " + f"{self.metrics.passed}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**❌ 失败用例： " + f"{self.metrics.failed}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**❗ 异常用例： " + f"{self.metrics.broken}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "**❓ 跳过用例： " + f"{self.metrics.skipped}" + "**"
                },
                {
                  "tag": "markdown",
                  "content": "📅 时间： " + f"{datetime.datetime.now().strftime('%Y-%m-%d')}"
                },
                {
                  "tag": "action",
                  "actions": [
                    {
                      "tag": "button",
                      "text": {
                        "tag": "plain_text",
                        "content": "报告详情"
                      },
                      "type": "primary",
                      "url": "https://mam-testcase-report.yiye.ai/"
                    }
                  ]
                }
              ],
              "header": {
                "template": header_color,
                "title": {
                  "content": header_text,
                  "tag": "plain_text"
                }
              }
            }
        }
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        post_data = json.dumps(rich_text)
        response = requests.post(
                config.feishu.webhook,
                headers=headers,
                data=post_data,
                verify=False
        )
        result = response.json()

        if result.get('StatusCode') != 0:
            time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            result_msg = result['errmsg'] if result.get('errmsg', False) else '未知异常'
            error_data = {
                "msgtype": "text",
                "text": {
                            "content": f"[注意-自动通知]飞书机器人消息发送失败，时间：{time_now}，"
                                       f"原因：{result_msg}，请及时跟进，谢谢!"
                },
                "at": {
                            "isAtAll": False
                        }
                    }
            logging.error("消息发送失败，自动通知：%s", error_data)
            requests.post(config.feishu.webhook, headers=headers, data=json.dumps(error_data))
        return result

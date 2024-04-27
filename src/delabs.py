from data import config
from src.utils import Web3Utils
from fake_useragent import UserAgent
import aiohttp
from src.utils import logger


class Delabs:
    def __init__(self, key: str, thread: int, proxy=None):
        self.web3_utils = Web3Utils(key=key)

        self.proxy = f"http://{proxy}" if proxy is not None else None
        self.thread = thread

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://app.delabs.gg",
            "Referer": "https://app.delabs.gg",
            'User-Agent': UserAgent(os='windows').random,
        }

        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, cookie_jar=aiohttp.CookieJar())

    async def logout(self):
        await self.session.close()

    async def login(self):
        json_data = {
            "loginType": "metamask",
            "signature": await self.get_signature(),
            "walletAddress": self.web3_utils.acct.address
        }

        resp = await self.session.post("https://app.delabs.gg/auth/login-wallet", json=json_data, proxy=self.proxy)
        self.session.cookie_jar.update_cookies(resp.cookies)
        return True

    async def get_signature(self):
        json_data = {"walletAddress": self.web3_utils.acct.address, "registerWallet": "metamask"}
        resp = await self.session.post("https://app.delabs.gg/auth/register-wallet", json=json_data, proxy=self.proxy)

        resp_json = await resp.json()
        msg = f"Please sign the message to verify your wallet. By signing the message, you are proving ownership of the connected wallet. This request will not trigger any blockchain transaction or cost any gas fee.\n\nNonce: {resp_json.get('nonce')}"

        return self.web3_utils.get_signed_code(msg)

    async def set_referrer(self):
        json_data = {"referral_code": config.REF_CODE}
        resp = await self.session.post("https://app.delabs.gg/mission/set-one-time-referral", json=json_data, proxy=self.proxy)

        return bool((await resp.json()).get("claimSuccess")) is True

    async def check_in(self):
        resp = await self.session.post("https://app.delabs.gg/mission/set-daily-checkin", proxy=self.proxy)

        return bool((await resp.json()).get("claimSuccess")) is True

    async def draw(self):
        resp = await self.session.post("https://app.delabs.gg/mission/set-daily-draw", proxy=self.proxy)

        return bool((await resp.json()).get("claimSuccess")) is True

    async def get_user_info(self):
        resp = await self.session.post("https://app.delabs.gg/mission/user-info", proxy=self.proxy)
        resp_json = (await resp.json()).get("userInfo")

        referral_code = resp_json.get("referral_code") if resp_json.get("referral_code") is not None else "-"
        referral_count = resp_json.get("referral_count") if resp_json.get("referral_count") is not None else 0
        total_points = resp_json.get("total_points") if resp_json.get("total_points") is not None else 0

        return [self.web3_utils.acct.address, referral_count, total_points, referral_code]

    async def sleep(self, seconds):
        logger.info(f"Thread {self.thread} | Sleep {round(seconds, 2)} second(s)!")

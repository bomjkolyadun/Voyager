import os.path
import time
import warnings
from typing import SupportsFloat, Any, Tuple, Dict

import requests
import json

import gymnasium as gym
from gymnasium.core import ObsType

import voyager.utils as U

from .minecraft_launcher import MinecraftInstance
from .process_monitor import SubprocessMonitor


class VoyagerEnv(gym.Env):
    def __init__(
        self,
        mc_port=None,
        azure_login=None,
        server_host="http://127.0.0.1",
        server_port=3000,
        request_timeout=600,
        log_path="./logs",
    ):
        if not mc_port and not azure_login:
            raise ValueError("Either mc_port or azure_login must be specified")
        if mc_port and azure_login:
            warnings.warn(
                "Both mc_port and mc_login are specified, mc_port will be ignored"
            )
        self.mc_port = mc_port
        self.azure_login = azure_login
        self.server = f"{server_host}:{server_port}"
        self.server_port = server_port
        self.request_timeout = request_timeout
        self.log_path = log_path
        self.mineflayer = self.get_mineflayer_process(server_port)
        if azure_login:
            self.mc_instance = self.get_mc_instance()
        else:
            self.mc_instance = None
        self.has_reset = False
        self.reset_options = None
        self.connected = False
        self.server_paused = False
        
        # Add restart tracking to prevent excessive restarts
        self.last_restart_time = 0
        self.restart_count = 0
        self.restart_cooldown = 5  # Minimum seconds between restarts
        self.consecutive_failures = 0  # Track consecutive failures for exponential backoff
        self.max_consecutive_failures = 5  # Maximum failures before giving up

    def get_mineflayer_process(self, server_port):
        U.f_mkdir(self.log_path, "mineflayer")
        file_path = os.path.abspath(os.path.dirname(__file__))
        return SubprocessMonitor(
            commands=[
                "node",
                U.f_join(file_path, "mineflayer/index.js"),
                str(server_port),
            ],
            name="mineflayer",
            ready_match=r"Server started on port (\d+)",
            log_path=U.f_join(self.log_path, "mineflayer"),
        )

    def get_mc_instance(self):
        print("Creating Minecraft server")
        U.f_mkdir(self.log_path, "minecraft")
        return MinecraftInstance(
            **self.azure_login,
            mineflayer=self.mineflayer,
            log_path=U.f_join(self.log_path, "minecraft"),
        )

    def check_process(self):
        if self.mc_instance and not self.mc_instance.is_running:
            # if self.mc_instance:
            #     self.mc_instance.check_process()
            #     if not self.mc_instance.is_running:
            print("Starting Minecraft server")
            self.mc_instance.run()
            self.mc_port = self.mc_instance.port
            self.reset_options["port"] = self.mc_instance.port
            print(f"Server started on port {self.reset_options['port']}")
        
        retry = 0
        max_retries = 3
        while not self.mineflayer.is_running:
            current_time = time.time()
            
            # Check consecutive failures for exponential backoff
            if self.consecutive_failures >= self.max_consecutive_failures:
                print(f"\033[31mToo many consecutive failures ({self.consecutive_failures}). Giving up.\033[0m")
                raise RuntimeError(f"Mineflayer failed to start after {self.consecutive_failures} consecutive failures")
            
            # Calculate delay based on consecutive failures (exponential backoff)
            base_delay = self.restart_cooldown * (2 ** min(self.consecutive_failures, 4))  # Cap at 16x
            
            # Check if we're restarting too frequently
            if current_time - self.last_restart_time < base_delay:
                remaining_cooldown = base_delay - (current_time - self.last_restart_time)
                print(f"\033[33mWaiting {remaining_cooldown:.1f}s cooldown before restart (consecutive failures: {self.consecutive_failures})...\033[0m")
                time.sleep(remaining_cooldown)
                current_time = time.time()
            
            retry += 1
            self.restart_count += 1
            self.last_restart_time = current_time
            print(f"\033[33mMineflayer process has exited, restarting (attempt {retry}/{max_retries}, total restarts: {self.restart_count}, consecutive failures: {self.consecutive_failures})\033[0m")
            
            if retry > max_retries:
                self.consecutive_failures += 1
                print(f"\033[31mMineflayer process failed to start after {max_retries} attempts\033[0m")
                raise RuntimeError("Mineflayer process failed to start")
            
            # Add delay to allow port to be freed
            if retry > 1:
                print(f"\033[33mWaiting 3 seconds for port {self.server_port} to be freed...\033[0m")
                time.sleep(3)
            
            # Check if port is still in use and kill any processes using it
            try:
                import subprocess
                result = subprocess.run(['lsof', '-ti', f':{self.server_port}'], 
                                     capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    print(f"\033[33mFound processes using port {self.server_port}: {pids}\033[0m")
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], check=True)
                            print(f"\033[33mKilled process {pid} using port {self.server_port}\033[0m")
                        except Exception as e:
                            print(f"\033[33mFailed to kill process {pid}: {e}\033[0m")
                    time.sleep(1)  # Additional wait after killing processes
            except Exception as e:
                print(f"\033[33mError checking port {self.server_port}: {e}\033[0m")
            
            try:
                self.mineflayer.run()
                
                if not self.mineflayer.is_running:
                    print(f"\033[31mMineflayer failed to start on attempt {retry}\033[0m")
                    continue
                    
                print(f"\033[32mMineflayer started successfully: {self.mineflayer.ready_line}\033[0m")
                
                # Try to connect to the Mineflayer server
                res = requests.post(
                    f"{self.server}/start",
                    json=self.reset_options,
                    timeout=self.request_timeout,
                )
                if res.status_code != 200:
                    print(f"\033[31mMinecraft server replied with code {res.status_code}: {res.text}\033[0m")
                    self.mineflayer.stop()
                    # Don't raise immediately, let the retry loop handle it
                    continue
                else:
                    print(f"\033[32mSuccessfully connected to Minecraft server\033[0m")
                    self.consecutive_failures = 0  # Reset on success
                    return res.json()
                    
            except Exception as e:
                print(f"\033[31mError during Mineflayer restart attempt {retry}: {e}\033[0m")
                if self.mineflayer.is_running:
                    self.mineflayer.stop()
                continue
        
        # If we get here, mineflayer is running but we haven't tried to connect yet
        try:
            res = requests.post(
                f"{self.server}/start",
                json=self.reset_options,
                timeout=self.request_timeout,
            )
            if res.status_code != 200:
                print(f"\033[31mMinecraft server replied with code {res.status_code}: {res.text}\033[0m")
                raise RuntimeError(
                    f"Minecraft server reply with code {res.status_code}"
                )
            return res.json()
        except Exception as e:
            print(f"\033[31mError connecting to Minecraft server: {e}\033[0m")
            raise

    def step(
        self,
        code: str,
        programs: str = "",
    ) -> Tuple[ObsType, SupportsFloat, bool, bool, Dict[str, Any]]:
        if not self.has_reset:
            raise RuntimeError("Environment has not been reset yet")
            
        # Only check process if it's actually not running
        if not self.mineflayer.is_running:
            print(f"\033[33mMineflayer is not running, checking process...\033[0m")
            self.check_process()
        
        self.unpause()
        data = {
            "code": code,
            "programs": programs,
        }
        res = requests.post(
            f"{self.server}/step", json=data, timeout=self.request_timeout
        )
        if res.status_code != 200:
            raise RuntimeError("Failed to step Minecraft server")
        returned_data = res.json()
        self.pause()
        return json.loads(returned_data)

    def render(self):
        raise NotImplementedError("render is not implemented")

    def reset(
        self,
        *,
        seed=None,
        options=None,
    ) -> Tuple[ObsType, Dict[str, Any]]:
        if options is None:
            options = {}

        if options.get("inventory", {}) and options.get("mode", "hard") != "hard":
            raise RuntimeError("inventory can only be set when options is hard")

        self.reset_options = {
            "port": self.mc_port,
            "reset": options.get("mode", "hard"),
            "inventory": options.get("inventory", {}),
            "equipment": options.get("equipment", []),
            "spread": options.get("spread", False),
            "waitTicks": options.get("wait_ticks", 5),
            "position": options.get("position", None),
        }

        self.unpause()
        
        # Stop mineflayer gracefully
        print(f"\033[33mResetting environment with mode: {options.get('mode', 'hard')}\033[0m")
        self.mineflayer.stop()
        time.sleep(2)  # Increased wait time for mineflayer to exit and free the port

        returned_data = self.check_process()
        self.has_reset = True
        self.connected = True
        # All the reset in step will be soft
        self.reset_options["reset"] = "soft"
        self.pause()
        return json.loads(returned_data)

    def close(self):
        self.unpause()
        if self.connected:
            res = requests.post(f"{self.server}/stop")
            if res.status_code == 200:
                self.connected = False
        if self.mc_instance:
            self.mc_instance.stop()
        self.mineflayer.stop()
        return not self.connected

    def pause(self):
        if self.mineflayer.is_running and not self.server_paused:
            res = requests.post(f"{self.server}/pause")
            if res.status_code == 200:
                self.server_paused = True
        return self.server_paused

    def unpause(self):
        if self.mineflayer.is_running and self.server_paused:
            res = requests.post(f"{self.server}/pause")
            if res.status_code == 200:
                self.server_paused = False
            else:
                print(res.json())
        return self.server_paused

    def health_check(self):
        """Perform a health check on the Voyager environment."""
        print("=== Voyager Environment Health Check ===")
        
        # Check Mineflayer process
        if self.mineflayer.is_running:
            print("✓ Mineflayer process is running")
        else:
            print("✗ Mineflayer process is not running")
        
        # Check server connectivity
        try:
            response = requests.get(f"{self.server}/health", timeout=5)
            if response.status_code == 200:
                print("✓ Mineflayer server is responding")
            else:
                print(f"✗ Mineflayer server returned status {response.status_code}")
        except Exception as e:
            print(f"✗ Cannot connect to Mineflayer server: {e}")
        
        # Check port usage
        try:
            import subprocess
            result = subprocess.run(['lsof', '-ti', f':{self.server_port}'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                print(f"✓ Port {self.server_port} is in use by PIDs: {pids}")
            else:
                print(f"✗ Port {self.server_port} is not in use")
        except Exception as e:
            print(f"? Cannot check port usage: {e}")
        
        # Check restart statistics
        print(f"📊 Restart count: {self.restart_count}")
        print(f"📊 Consecutive failures: {self.consecutive_failures}")
        if self.last_restart_time > 0:
            time_since_restart = time.time() - self.last_restart_time
            print(f"📊 Time since last restart: {time_since_restart:.1f}s")
        
        print("=== End Health Check ===")

    def send_chat_message(self, message, sender="Human"):
        """Send a chat message to the bot."""
        if not self.mineflayer.is_running:
            print("⚠️  Mineflayer is not running. Cannot send chat message.")
            return False
            
        try:
            data = {
                "message": message,
                "sender": sender
            }
            res = requests.post(f"{self.server}/chat", json=data, timeout=10)
            if res.status_code == 200:
                print(f"✅ Chat message sent: {sender}: {message}")
                return True
            else:
                print(f"❌ Failed to send chat message: {res.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error sending chat message: {e}")
            return False

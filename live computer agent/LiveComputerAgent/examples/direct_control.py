from live_computer_agent.config import Config
from live_computer_agent.core.engine import LiveComputerAgent
with_agent=LiveComputerAgent(Config.load())
try:
 print(with_agent.start('direct'));print(with_agent.observe(True));print(with_agent.perform('hotkey',True,keys='ctrl+l'))
finally:print(with_agent.stop())

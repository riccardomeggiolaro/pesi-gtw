# ===============================================================
# App.: PES001
# TEMPLATE APPLICATIVO
# ===============================================================
import time

import lb_log
import lb_config

def init():
	lb_log.info("app.init")

# Worker principale
def wrk_main():
	secwait=0.5
	while lb_config.g_enabled:
		time.sleep(secwait)

	lb_log.info("PES001:end")

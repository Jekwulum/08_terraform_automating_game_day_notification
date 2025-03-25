# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(function_app) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints

import azure.functions as func
import logging
from nba_notifications import GameDayNotification

app = func.FunctionApp()
function_app = func.Blueprint()


@function_app.timer_trigger(schedule="0 */2 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def GameDayFuncApp(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    game_day_notification = GameDayNotification()
    data = game_day_notification.fetch_sports_data()
    game_day_notification.publish_to_topic(data)

app.register_functions(function_app)
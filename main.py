from gym_reservation_bot import GymReservationBot
import functions_framework

@functions_framework.http
def make_reservation(request):
    """HTTP Cloud Function that runs the gym reservation bot"""
    try:
        bot = GymReservationBot()
        bot.run()
        return 'Reservation attempt completed', 200
    except Exception as e:
        return f'Error: {str(e)}', 500
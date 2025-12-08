from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages


class SessionMiddleware(MiddlewareMixin):
    """
    Custom middleware to handle session expiry and auto-logout
    """
    
    def process_request(self, request):
        """Check session validity on each request"""
        # Check if session has expired
        if 'logged_in' in request.session:
            # Session is valid
            pass
        elif 'user_id' in request.session:
            # Old session without logged_in flag
            # User is still logged in from before update
            request.session['logged_in'] = True
        
        return None


class AutoLogoutMiddleware(MiddlewareMixin):
    """
    Logs out user after a period of inactivity
    """
    
    def process_request(self, request):
        """Check for session timeout"""
        if 'last_activity' in request.session:
            import datetime
            last_activity = request.session.get('last_activity')
            
            # Check if session has been inactive for more than 30 minutes (1800 seconds)
            if isinstance(last_activity, str):
                from django.utils import timezone
                last_activity = timezone.datetime.fromisoformat(last_activity)
            
            # Only if user is logged in
            if request.session.get('logged_in'):
                from django.utils import timezone
                import datetime as dt
                now = timezone.now()
                timeout = dt.timedelta(seconds=1800)  # 30 minutes
                
                if last_activity and (now - last_activity) > timeout:
                    # Session expired, log out
                    request.session.flush()
                    messages.warning(request, 'Your session has expired. Please log in again.')
                    return redirect('/schoolApp/login/')
        
        # Update last activity
        from django.utils import timezone
        request.session['last_activity'] = timezone.now().isoformat()
        
        return None

"""Demo adapter for ODIN control workshop

This class implements a simple adapter used for demonstration purposes in a

Tim Nicholls, STFC Application Engineering
"""
import logging
import tornado  #type: ignore
import time
import sys
from concurrent import futures

from tornado.ioloop import IOLoop, PeriodicCallback # type: ignore
from tornado.concurrent import run_on_executor # type: ignore
from tornado.escape import json_decode # type: ignore

from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types # type: ignore
from odin.adapters.parameter_tree import ParameterTree, ParameterTreeError # type: ignore
from odin._version import get_versions # type: ignore


class JacksAdapter(ApiAdapter):
    """System info adapter class for the ODIN server.

    This adapter provides ODIN clients with information about the server and the system that it is
    running on.
    """

    def __init__(self, **kwargs):
        """Initialize the WorkshopAdapter object.

        This constructor initializes the WorkshopAdapter object.

        :param kwargs: keyword arguments specifying options
        """
        # Intialise superclass
        super(JacksAdapter, self).__init__(**kwargs)

        # Parse options
        background_task_enable = bool(self.options.get('background_task_enable', False))
        background_task_interval = float(self.options.get('background_task_interval', 1.0))

        self.jacksAdapter = Workshop(background_task_enable, background_task_interval)

        logging.debug('WorkshopAdapter loaded')

    @response_types('application/json', default='application/json')
    def get(self, path, request):
        """Handle an HTTP GET request.

        This method handles an HTTP GET request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        try:
            response = self.jacksAdapter.get(path)
            status_code = 200
        except ParameterTreeError as e:
            response = {'error': str(e)}
            status_code = 400

        content_type = 'application/json'

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def put(self, path, request):
        """Handle an HTTP PUT request.

        This method handles an HTTP PUT request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """

        content_type = 'application/json'

        try:
            data = json_decode(request.body)
            self.jacksAdapter.set(path, data)
            response = self.jacksAdapter.get(path)
            status_code = 200
        except WorkshopError as e:
            response = {'error': str(e)}
            status_code = 400
        except (TypeError, ValueError) as e:
            response = {'error': 'Failed to decode PUT request body: {}'.format(str(e))}
            status_code = 400

        logging.debug(response)

        return ApiAdapterResponse(response, content_type=content_type,
                                  status_code=status_code)

    def delete(self, path, request):
        """Handle an HTTP DELETE request.

        This method handles an HTTP DELETE request, returning a JSON response.

        :param path: URI path of request
        :param request: HTTP request object
        :return: an ApiAdapterResponse object containing the appropriate response
        """
        response = 'WorkshopAdapter: DELETE on path {}'.format(path)
        status_code = 200

        logging.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)

    def cleanup(self):
        """Clean up adapter state at shutdown.

        This method cleans up the adapter state when called by the server at e.g. shutdown.
        It simplied calls the cleanup function of the jacksAdapter instance.
        """
        self.jacksAdapter.cleanup()

class WorkshopError(Exception):
    """Simple exception class to wrap lower-level exceptions."""

    pass


class Workshop():
    """Workshop - class that extracts and stores information about system-level parameters."""

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self, background_task_enable, background_task_interval):
        """Initialise the Workshop object.

        This constructor initlialises the Workshop object, building a parameter tree and
        launching a background task if enabled
        """
        # Save arguments
        self.background_task_enable = background_task_enable
        self.background_task_interval = background_task_interval

        # Store initialisation time
        self.init_time = time.time()

        # Get package version information
        version_info = get_versions()

        # Set the background task counters to zero
        self.background_ioloop_counter = 0
        self.background_thread_counter = 0
        self.my_parameter_times_called = 0
        self.my_settable_parameter_times_called = 0
        self.my_settable_parameter_2 = 0
        self.my_settable_parameter_text = "Hello"
        self.my_settable_parameter_mode = "Mode1"

        # Build a parameter tree for the background task
        bg_task = ParameterTree({
            'ioloop_count': (lambda: self.background_ioloop_counter, None),
            'thread_count': (lambda: self.background_thread_counter, None),
            'enable': (lambda: self.background_task_enable, self.set_task_enable),
            'interval': (lambda: self.background_task_interval, self.set_task_interval),
        })
        
        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'odin_version': version_info['version'],
            'tornado_version': tornado.version,
            'server_uptime': (self.get_server_uptime, None),
            'background_task': bg_task,
            'my_parameter': (self.get_my_parameter, None),
            'my_settable_parameter': (self.get_my_settable_parameter, self.set_my_settable_parameter),
            'my_settable_parameter_2': (self.get_my_settable_parameter_2, self.set_my_settable_parameter_2),
            'my_settable_parameter_text': (self.get_my_settable_parameter_text, self.set_my_settable_parameter_text),
            'my_settable_parameter_mode': (self.get_my_settable_parameter_mode, self.set_my_settable_parameter_mode)
        })

        # Launch the background task if enabled in options
        if self.background_task_enable:
            self.start_background_tasks()

    def get_server_uptime(self):
        """Get the uptime for the ODIN server.

        This method returns the current uptime for the ODIN server.
        """
        return time.time() - self.init_time
    
    def get_my_parameter(self):
        #function I added to see if I could
        self.my_parameter_times_called += 1
        return self.my_parameter_times_called
    
    def get_my_settable_parameter(self):
        #function I added to see if I could
        return self.my_settable_parameter_times_called
    
    def set_my_settable_parameter(self, parameter_value):
        #function I added to see if I could
        self.my_settable_parameter_times_called = parameter_value
        
    def get_my_settable_parameter_2(self):
        #function I added to see if I could
        return self.my_settable_parameter_2
    
    def set_my_settable_parameter_2(self, parameter_value):
        #function I added to see if I could
        self.my_settable_parameter_2 = parameter_value
    
    def get_my_settable_parameter_text(self):
        #function I added to see if I could
        return self.my_settable_parameter_text
    
    def set_my_settable_parameter_text(self, parameter_value):
        #function I added to see if I could
        self.my_settable_parameter_text = parameter_value
        
    def get_my_settable_parameter_mode(self):
        #function I added to see if I could
        return self.my_settable_parameter_mode
    
    def set_my_settable_parameter_mode(self, parameter_value):
        #function I added to see if I could
        self.my_settable_parameter_mode = parameter_value

    def get(self, path):
        """Get the parameter tree.

        This method returns the parameter tree for use by clients via the Workshop adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def set(self, path, data):
        """Set parameters in the parameter tree.

        This method simply wraps underlying ParameterTree method so that an exceptions can be
        re-raised with an appropriate WorkshopError.

        :param path: path of parameter tree to set values for
        :param data: dictionary of new data values to set in the parameter tree
        """
        try:
            self.param_tree.set(path, data)
        except ParameterTreeError as e:
            raise WorkshopError(e)

    def cleanup(self):
        """Clean up the Workshop instance.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        self.stop_background_tasks()

    def set_task_interval(self, interval):
        """Set the background task interval."""
        logging.debug("Setting background task interval to %f", interval)
        self.background_task_interval = float(interval)
        
    def set_task_enable(self, enable):
        """Set the background task enable."""
        enable = bool(enable)

        if enable != self.background_task_enable:
            if enable:
                self.start_background_tasks()
            else:
                self.stop_background_tasks()

    def start_background_tasks(self):
        """Start the background tasks."""
        logging.debug(
            "Launching background tasks with interval %.2f secs", self.background_task_interval
        )

        self.background_task_enable = True

        # Register a periodic callback for the ioloop task and start it
        self.background_ioloop_task = PeriodicCallback(
            self.background_ioloop_callback, self.background_task_interval * 1000
        )
        self.background_ioloop_task.start()

        # Run the background thread task in the thread execution pool
        self.background_thread_task()

    def stop_background_tasks(self):
        """Stop the background tasks."""
        self.background_task_enable = False
        self.background_ioloop_task.stop()

    def background_ioloop_callback(self):
        """Run the adapter background IOLoop callback.

        This simply increments the background counter before returning. It is called repeatedly
        by the periodic callback on the IOLoop.
        """

        #if self.background_ioloop_counter < 10 or self.background_ioloop_counter % 20 == 0:
            #logging.debug(
                #"Background IOLoop task running, count = %d", self.background_ioloop_counter
            #)

        self.background_ioloop_counter += 1

    @run_on_executor
    def background_thread_task(self):
        """The the adapter background thread task.

        This method runs in the thread executor pool, sleeping for the specified interval and 
        incrementing its counter once per loop, until the background task enable is set to false.
        """

        sleep_interval = self.background_task_interval

        while self.background_task_enable:
            time.sleep(sleep_interval)
            #if self.background_thread_counter < 10 or self.background_thread_counter % 20 == 0:
                #logging.debug(
                    #"Background thread task running, count = %d", self.background_thread_counter
                #)
            self.background_thread_counter += 1

        logging.debug("Background thread task stopping")

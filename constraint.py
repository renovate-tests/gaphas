"""equation solver using attributes and introspection.

Class Constraint from
   http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/303396
"""

__version__ = "$Revision$"
# $HeadURL$

from __future__ import division

TOL = 0.0000001      # tolerance
ITERLIMIT = 1000        # iteration limit

class Constraint(object):
    """takes a function, named arg value (opt.) and returns a Constraint object
    """
    
    def __init__(self, f, **args):
        self._f = f
        self._args = {}
        # see important note on order of operations in __setattr__ below.
        for arg in f.func_code.co_varnames[0:f.func_code.co_argcount]:
            self._args[arg] = None
        self.set(**args)

    def __repr__(self):
        argstring = ', '.join(['%s=%s' % (arg, str(value)) for (arg, value) in
                             self._args.items()])
        if argstring:
            return 'Constraint(%s, %s)' % (self._f.func_code.co_name, argstring)
        else:
            return 'Constraint(%s)' % self._f.func_code.co_name

    def __getattr__(self, name):
        """used to extract function argument values
        """
        self._args[name]
        return self.solve_for(name)

    def __setattr__(self, name, value):
        """sets function argument values"""
        # Note - once self._args is created, no new attributes can
        # be added to self.__dict__.  This is a good thing as it throws
        # an exception if you try to assign to an arg which is inappropriate
        # for the function in the solver.
        if self.__dict__.has_key('_args'):
            if name in self._args:
                self._args[name] = value
            else:
                raise KeyError, name
        else:
            object.__setattr__(self, name, value)

    def set(self, **args):
        """sets values of function arguments"""
        for arg in args:
            self._args[arg]  # raise exception if arg not in _args
            setattr(self, arg, args[arg])

    def solve_for(self, arg):
        """Newton's method solver"""
        args = self._args
        close_runs = 10   # after getting close, do more passes
        if self._args[arg]:
            x0 = self._args[arg]
        else:
            x0 = 1
        if x0 == 0:
            x1 = 1
        else:
            x1 = x0*1.1
        def f(x):
            """function to solve"""
            args[arg] = x
            return self._f(**args)
        fx0 = f(x0)
        n = 0
        while 1:                    # Newton's method loop here
            fx1 = f(x1)
            if fx1 == 0 or x1 == x0:  # managed to nail it exactly
                break
            if abs(fx1-fx0) < TOL:    # very close
                close_flag = True
                if close_runs == 0:       # been close several times
                    break
                else:
                    close_runs -= 1       # try some more
            else:
                close_flag = False
            if n > ITERLIMIT:
                print "Failed to converge; exceeded iteration limit"
                break
            slope = (fx1 - fx0) / (x1 - x0)
            if slope == 0:
                if close_flag:  # we're close but have zero slope, finish
                    break
                else:
                    print 'Zero slope and not close enough to solution'
                    break
            x2 = x0 - fx0 / slope           # New 'x1'
            fx0 = fx1
            x0 = x1
            x1 = x2
            n += 1
        self._args[arg] = x1
        return x1



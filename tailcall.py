"""Python is not optimize tail recursion As a result, a trampoline
can be used to circumvent this pitfall. The following is an attempt to
implement a trampoline."""

# Demonstration of tail call stack explosion

def fact(n, r=1):
	if n <= 1:
		return n
	return fact(n-1, n*r)

try:
	fact(100000)
except RuntimeError, e:
	print 'Despite tail recursive calls, python still blows the stack.'


# First attempt at trampoline

class TailCall_(object):
	def __init__(self, f, *args, **kwargs):
		self.f = f
		self.args = args
		self.kwargs = kwargs

	def handle(self):
		return self.f(*self.args, **self.kwargs)

def tail_wrap(f):
	def _f(*args, **kwargs):
		r = f(*args, **kwargs)
		while type(r) is TailCall_:
			r = r.handle()
		return r
	return _f

# @tail_wrap # fact = tail_wrap(fact)
def fact(n, r=1):
	if n <= 1:
		return r
	return TailCall_(fact, n-1, n*r)	

try:
	print 'First attempt - tail_wrap(fact)(100000):', tail_wrap(fact)(100)
except RuntimeError, e:
	print 'The trampoline doesn\'t work!'

# Note: tail_wrap can't be used as a wrapper because then the wrapper
# function is trampolined to as opposed to fact. This is because
# fact_tramp gets redefined as fact_tramp = tail_wrap(fact_tramp)


# Second attempt at trampoline

class TailCall(object):
	def __init__(self, f, *args, **kwargs):
		self.f = f
		self.args = args
		self.kwargs = kwargs

	def handle(self):
		if type(self.f) is TailCaller:
			return self.f.f(*self.args, **self.kwargs)
		return self.f(*self.args, **self.kwargs)

class TailCaller(object):
	def __init__(self, f):
		self.f = f

	# Called when the wrapped function is invoked (once below)
	def __call__(self, *args, **kwargs):
		r = self.f(*args, **kwargs)
		while type(r) is TailCall:
			r = r.handle()
		return r

@TailCaller
def fact(n, r=1):
	if n <= 1:
		return r
	return TailCall(fact, n-1, n*r)

fact = TailCall(fact)

try:
	print 'Second attempt - fact(333):', fact(333)
except RuntimeError, e:
	print 'Solution 2 is a bad solution!'

# This is nearly identical to solution 1 but TailCall uses the TailCaller
# type to determine whether it should call the function that is wrapped (fact)
# as opposed to the TailCaller object.

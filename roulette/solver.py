from z3 import *

def solve(current_cash):

  x = BitVec('x', 64)
  c = BitVec('c', 64)

  init_cash = BitVecVal(current_cash, 32)
  bet    = BitVec('bet', 32)
  cash   = BitVec('cash', 32)

  opt = Optimize()

  MAX_LONG = 2**31 - 1

  # x is positive
  opt.add(x >= 0)
  opt.add(x <= MAX_LONG)

  # c is a single digit
  opt.add(c >= 0)
  opt.add(c <= 9)

  def int64_to_int32(x):
    return Extract(31, 0, x)

  opt.add(bet == int64_to_int32(x * 10 + c))

  # the result after parsing is less than our current cash
  opt.add(bet <= init_cash)

  # positive minus a negative is positive ;)
  opt.add(cash == init_cash - bet)

  opt.add(cash == 1000000001)

#  print('MAX_LONG = %s' %  MAX_LONG)

  # maximize the final number
  h = opt.maximize(cash)

  opt.check()
#  print(opt.check())
  m = opt.model()

  x_val = int(str(m[x]))
  c_val = int(str(m[c]))

  return x_val*10 + c_val

#def debug_model(m):
#  print("init_cash %s \t %s" % (init_cash, m.evaluate(BV2Int(init_cash, is_signed=True))))
#  print("x         %s \t %s" % (m[x], m.evaluate(BV2Int(x, is_signed=True))))
#  print("c         %s \t %s" % (m[c], m.evaluate(BV2Int(c, is_signed=True))))
#  #print("bet       %s \t %s" % (m[bet], m.evaluate(BV2Int(bet, is_signed=True))))
#  print("cash      %s \t %s" % (m[cash], m.evaluate(BV2Int(cash, is_signed=True) )) )




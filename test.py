
from docplex.cp.model import CpoModel

model = CpoModel()
x = model.integer_var(min=0, max=10, name="x")
y = model.integer_var(min=0, max=10, name="y")

model.add(x + y >= 10)
model.maximize(x + 2 * y)

solution = model.solve()

print("x =", solution.get_value(x))
print("y =", solution.get_value(y))
print("Objective =", solution.get_objective_value())

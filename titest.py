import taichi as ti

ti.init(arch=ti.gpu)  # Try to run on GPU


@ti.data_oriented
class MyClass:

    @ti.kernel
    def inc(self, temp: ti.template()):

        #increment all elements in array by 1
        for I in ti.grouped(temp):
            temp[I] += 1

    def call_inc(self):
        self.inc(self.temp)

    def allocate_temp(self, n):
        self.temp = ti.field(dtype=ti.i32, shape=n)


@ti.data_oriented
class FEM:

    # @ti.kernel
    def __init__(self) -> None:
        a = MyClass()  # creating an instance of Data-Oriented Class

        # a.call_inc() cannot be called, because a.temp has not been allocated at this point
        a.allocate_temp(4)  # [0 0 0 0]
        a.call_inc()  # [1 1 1 1]
        a.call_inc()  # [2 2 2 2]
        print(a.temp)  # will print [2 2 2 2]

        a.allocate_temp(8)  # [0 0 0 0 0 0 0 0 0]
        a.call_inc()  # [1 1 1 1 1 1 1 1]
        print(a.temp)  # will print [1 1 1 1 1 1 1 1]

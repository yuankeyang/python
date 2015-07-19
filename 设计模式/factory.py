#python工厂模式

'''|--------------------|
| 运算类             |
|--------------------||+NumberA:double     |
|+NumberB:double     |
|--------------------||+GetResult():double |
|--------------------|
'''class Operation:	def GetResult(self):		pass#加法类class OperationAdd(Operation):	def GetResult(self):		return self.op1+self.op2#减法类class OperationSub(Operation):	def GetResult(self):		return self.op1-self.op2#乘法类class OperationMul(Operation):	def GetResult(self):		return self.op1*self.op2#除法类class OperationDiv(Operation):	def GetResult(self):		try:			result=self.op1/self.op2			return result		except:			print("error:divided by zero.")			return 0#操作未定义class OperationUndef(Operation):	def GetResult(self):		print("Undefine Operation.")		return 0#工厂类class OperationFactory:	operation={}	operation["+"]=OperationAdd()	operation["-"]=OperationSub()	operation["*"]=OperationSub()	operation["/"]=OperationDiv()	def createOperation(self,ch):		if ch in self.operation:			op=self.operation[ch]		else:			op=OperationUndef()		return op

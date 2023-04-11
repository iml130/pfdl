# Generated from PFDLParser.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .PFDLParser import PFDLParser
else:
    from PFDLParser import PFDLParser

# This class defines a complete listener for a parse tree produced by PFDLParser.
class PFDLParserListener(ParseTreeListener):

    # Enter a parse tree produced by PFDLParser#program.
    def enterProgram(self, ctx:PFDLParser.ProgramContext):
        pass

    # Exit a parse tree produced by PFDLParser#program.
    def exitProgram(self, ctx:PFDLParser.ProgramContext):
        pass


    # Enter a parse tree produced by PFDLParser#struct.
    def enterStruct(self, ctx:PFDLParser.StructContext):
        pass

    # Exit a parse tree produced by PFDLParser#struct.
    def exitStruct(self, ctx:PFDLParser.StructContext):
        pass


    # Enter a parse tree produced by PFDLParser#task.
    def enterTask(self, ctx:PFDLParser.TaskContext):
        pass

    # Exit a parse tree produced by PFDLParser#task.
    def exitTask(self, ctx:PFDLParser.TaskContext):
        pass


    # Enter a parse tree produced by PFDLParser#task_in.
    def enterTask_in(self, ctx:PFDLParser.Task_inContext):
        pass

    # Exit a parse tree produced by PFDLParser#task_in.
    def exitTask_in(self, ctx:PFDLParser.Task_inContext):
        pass


    # Enter a parse tree produced by PFDLParser#task_out.
    def enterTask_out(self, ctx:PFDLParser.Task_outContext):
        pass

    # Exit a parse tree produced by PFDLParser#task_out.
    def exitTask_out(self, ctx:PFDLParser.Task_outContext):
        pass


    # Enter a parse tree produced by PFDLParser#statement.
    def enterStatement(self, ctx:PFDLParser.StatementContext):
        pass

    # Exit a parse tree produced by PFDLParser#statement.
    def exitStatement(self, ctx:PFDLParser.StatementContext):
        pass


    # Enter a parse tree produced by PFDLParser#service_call.
    def enterService_call(self, ctx:PFDLParser.Service_callContext):
        pass

    # Exit a parse tree produced by PFDLParser#service_call.
    def exitService_call(self, ctx:PFDLParser.Service_callContext):
        pass


    # Enter a parse tree produced by PFDLParser#task_call.
    def enterTask_call(self, ctx:PFDLParser.Task_callContext):
        pass

    # Exit a parse tree produced by PFDLParser#task_call.
    def exitTask_call(self, ctx:PFDLParser.Task_callContext):
        pass


    # Enter a parse tree produced by PFDLParser#call_input.
    def enterCall_input(self, ctx:PFDLParser.Call_inputContext):
        pass

    # Exit a parse tree produced by PFDLParser#call_input.
    def exitCall_input(self, ctx:PFDLParser.Call_inputContext):
        pass


    # Enter a parse tree produced by PFDLParser#call_output.
    def enterCall_output(self, ctx:PFDLParser.Call_outputContext):
        pass

    # Exit a parse tree produced by PFDLParser#call_output.
    def exitCall_output(self, ctx:PFDLParser.Call_outputContext):
        pass


    # Enter a parse tree produced by PFDLParser#parallel.
    def enterParallel(self, ctx:PFDLParser.ParallelContext):
        pass

    # Exit a parse tree produced by PFDLParser#parallel.
    def exitParallel(self, ctx:PFDLParser.ParallelContext):
        pass


    # Enter a parse tree produced by PFDLParser#while_loop.
    def enterWhile_loop(self, ctx:PFDLParser.While_loopContext):
        pass

    # Exit a parse tree produced by PFDLParser#while_loop.
    def exitWhile_loop(self, ctx:PFDLParser.While_loopContext):
        pass


    # Enter a parse tree produced by PFDLParser#counting_loop.
    def enterCounting_loop(self, ctx:PFDLParser.Counting_loopContext):
        pass

    # Exit a parse tree produced by PFDLParser#counting_loop.
    def exitCounting_loop(self, ctx:PFDLParser.Counting_loopContext):
        pass


    # Enter a parse tree produced by PFDLParser#condition.
    def enterCondition(self, ctx:PFDLParser.ConditionContext):
        pass

    # Exit a parse tree produced by PFDLParser#condition.
    def exitCondition(self, ctx:PFDLParser.ConditionContext):
        pass


    # Enter a parse tree produced by PFDLParser#condition_passed.
    def enterCondition_passed(self, ctx:PFDLParser.Condition_passedContext):
        pass

    # Exit a parse tree produced by PFDLParser#condition_passed.
    def exitCondition_passed(self, ctx:PFDLParser.Condition_passedContext):
        pass


    # Enter a parse tree produced by PFDLParser#condition_failed.
    def enterCondition_failed(self, ctx:PFDLParser.Condition_failedContext):
        pass

    # Exit a parse tree produced by PFDLParser#condition_failed.
    def exitCondition_failed(self, ctx:PFDLParser.Condition_failedContext):
        pass


    # Enter a parse tree produced by PFDLParser#parameter.
    def enterParameter(self, ctx:PFDLParser.ParameterContext):
        pass

    # Exit a parse tree produced by PFDLParser#parameter.
    def exitParameter(self, ctx:PFDLParser.ParameterContext):
        pass


    # Enter a parse tree produced by PFDLParser#struct_initialization.
    def enterStruct_initialization(self, ctx:PFDLParser.Struct_initializationContext):
        pass

    # Exit a parse tree produced by PFDLParser#struct_initialization.
    def exitStruct_initialization(self, ctx:PFDLParser.Struct_initializationContext):
        pass


    # Enter a parse tree produced by PFDLParser#variable_definition.
    def enterVariable_definition(self, ctx:PFDLParser.Variable_definitionContext):
        pass

    # Exit a parse tree produced by PFDLParser#variable_definition.
    def exitVariable_definition(self, ctx:PFDLParser.Variable_definitionContext):
        pass


    # Enter a parse tree produced by PFDLParser#primitive.
    def enterPrimitive(self, ctx:PFDLParser.PrimitiveContext):
        pass

    # Exit a parse tree produced by PFDLParser#primitive.
    def exitPrimitive(self, ctx:PFDLParser.PrimitiveContext):
        pass


    # Enter a parse tree produced by PFDLParser#attribute_access.
    def enterAttribute_access(self, ctx:PFDLParser.Attribute_accessContext):
        pass

    # Exit a parse tree produced by PFDLParser#attribute_access.
    def exitAttribute_access(self, ctx:PFDLParser.Attribute_accessContext):
        pass


    # Enter a parse tree produced by PFDLParser#array.
    def enterArray(self, ctx:PFDLParser.ArrayContext):
        pass

    # Exit a parse tree produced by PFDLParser#array.
    def exitArray(self, ctx:PFDLParser.ArrayContext):
        pass


    # Enter a parse tree produced by PFDLParser#number.
    def enterNumber(self, ctx:PFDLParser.NumberContext):
        pass

    # Exit a parse tree produced by PFDLParser#number.
    def exitNumber(self, ctx:PFDLParser.NumberContext):
        pass


    # Enter a parse tree produced by PFDLParser#value.
    def enterValue(self, ctx:PFDLParser.ValueContext):
        pass

    # Exit a parse tree produced by PFDLParser#value.
    def exitValue(self, ctx:PFDLParser.ValueContext):
        pass


    # Enter a parse tree produced by PFDLParser#expression.
    def enterExpression(self, ctx:PFDLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by PFDLParser#expression.
    def exitExpression(self, ctx:PFDLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by PFDLParser#binOperation.
    def enterBinOperation(self, ctx:PFDLParser.BinOperationContext):
        pass

    # Exit a parse tree produced by PFDLParser#binOperation.
    def exitBinOperation(self, ctx:PFDLParser.BinOperationContext):
        pass


    # Enter a parse tree produced by PFDLParser#unOperation.
    def enterUnOperation(self, ctx:PFDLParser.UnOperationContext):
        pass

    # Exit a parse tree produced by PFDLParser#unOperation.
    def exitUnOperation(self, ctx:PFDLParser.UnOperationContext):
        pass


    # Enter a parse tree produced by PFDLParser#json_object.
    def enterJson_object(self, ctx:PFDLParser.Json_objectContext):
        pass

    # Exit a parse tree produced by PFDLParser#json_object.
    def exitJson_object(self, ctx:PFDLParser.Json_objectContext):
        pass


    # Enter a parse tree produced by PFDLParser#pair.
    def enterPair(self, ctx:PFDLParser.PairContext):
        pass

    # Exit a parse tree produced by PFDLParser#pair.
    def exitPair(self, ctx:PFDLParser.PairContext):
        pass


    # Enter a parse tree produced by PFDLParser#json_open_bracket.
    def enterJson_open_bracket(self, ctx:PFDLParser.Json_open_bracketContext):
        pass

    # Exit a parse tree produced by PFDLParser#json_open_bracket.
    def exitJson_open_bracket(self, ctx:PFDLParser.Json_open_bracketContext):
        pass


    # Enter a parse tree produced by PFDLParser#json_value.
    def enterJson_value(self, ctx:PFDLParser.Json_valueContext):
        pass

    # Exit a parse tree produced by PFDLParser#json_value.
    def exitJson_value(self, ctx:PFDLParser.Json_valueContext):
        pass


    # Enter a parse tree produced by PFDLParser#json_array.
    def enterJson_array(self, ctx:PFDLParser.Json_arrayContext):
        pass

    # Exit a parse tree produced by PFDLParser#json_array.
    def exitJson_array(self, ctx:PFDLParser.Json_arrayContext):
        pass



del PFDLParser
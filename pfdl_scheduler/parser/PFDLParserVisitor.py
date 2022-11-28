# Generated from PFDLParser.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .PFDLParser import PFDLParser
else:
    from PFDLParser import PFDLParser

# This class defines a complete generic visitor for a parse tree produced by PFDLParser.

class PFDLParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PFDLParser#program.
    def visitProgram(self, ctx:PFDLParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#struct.
    def visitStruct(self, ctx:PFDLParser.StructContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#task.
    def visitTask(self, ctx:PFDLParser.TaskContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#task_in.
    def visitTask_in(self, ctx:PFDLParser.Task_inContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#task_out.
    def visitTask_out(self, ctx:PFDLParser.Task_outContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#statement.
    def visitStatement(self, ctx:PFDLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#service_call.
    def visitService_call(self, ctx:PFDLParser.Service_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#task_call.
    def visitTask_call(self, ctx:PFDLParser.Task_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#call_input.
    def visitCall_input(self, ctx:PFDLParser.Call_inputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#call_output.
    def visitCall_output(self, ctx:PFDLParser.Call_outputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#parallel.
    def visitParallel(self, ctx:PFDLParser.ParallelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#while_loop.
    def visitWhile_loop(self, ctx:PFDLParser.While_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#counting_loop.
    def visitCounting_loop(self, ctx:PFDLParser.Counting_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#condition.
    def visitCondition(self, ctx:PFDLParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#condition_passed.
    def visitCondition_passed(self, ctx:PFDLParser.Condition_passedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#condition_failed.
    def visitCondition_failed(self, ctx:PFDLParser.Condition_failedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#parameter.
    def visitParameter(self, ctx:PFDLParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#struct_initialization.
    def visitStruct_initialization(self, ctx:PFDLParser.Struct_initializationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#variable_definition.
    def visitVariable_definition(self, ctx:PFDLParser.Variable_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#primitive.
    def visitPrimitive(self, ctx:PFDLParser.PrimitiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#attribute_access.
    def visitAttribute_access(self, ctx:PFDLParser.Attribute_accessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#array.
    def visitArray(self, ctx:PFDLParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#number.
    def visitNumber(self, ctx:PFDLParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#value.
    def visitValue(self, ctx:PFDLParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#expression.
    def visitExpression(self, ctx:PFDLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#binOperation.
    def visitBinOperation(self, ctx:PFDLParser.BinOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#unOperation.
    def visitUnOperation(self, ctx:PFDLParser.UnOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#json_object.
    def visitJson_object(self, ctx:PFDLParser.Json_objectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#pair.
    def visitPair(self, ctx:PFDLParser.PairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#json_open_bracket.
    def visitJson_open_bracket(self, ctx:PFDLParser.Json_open_bracketContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#json_value.
    def visitJson_value(self, ctx:PFDLParser.Json_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PFDLParser#json_array.
    def visitJson_array(self, ctx:PFDLParser.Json_arrayContext):
        return self.visitChildren(ctx)



del PFDLParser
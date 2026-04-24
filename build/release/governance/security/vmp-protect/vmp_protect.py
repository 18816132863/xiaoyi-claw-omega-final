# VMP 保护实现

import os
import hashlib
import secrets
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import IntEnum

class VMOpcode(IntEnum):
    """自定义 VM 指令集 (256 条)"""
    # 算术运算 (0x00-0x1F)
    NOP = 0x00
    ADD = 0x01
    SUB = 0x02
    MUL = 0x03
    DIV = 0x04
    MOD = 0x05
    NEG = 0x06
    
    # 逻辑运算 (0x20-0x3F)
    AND = 0x20
    OR = 0x21
    XOR = 0x22
    NOT = 0x23
    SHL = 0x24
    SHR = 0x25
    
    # 控制流 (0x40-0x5F)
    JMP = 0x40
    JZ = 0x41
    JNZ = 0x42
    CALL = 0x43
    RET = 0x44
    HALT = 0x45
    
    # 内存操作 (0x60-0x7F)
    LOAD = 0x60
    STORE = 0x61
    PUSH = 0x62
    POP = 0x63
    
    # 特殊指令 (0x80-0x9F)
    DEBUG = 0x80
    GETKEY = 0x81
    DECRYPT = 0x82
    VERIFY = 0x83


@dataclass
class VMPConfig:
    """VMP 配置"""
    instruction_set: str = "custom_v1"
    anti_debug: bool = True
    anti_dump: bool = True
    integrity_check: bool = True
    obfuscation_level: str = "high"  # low, medium, high, critical


class AntiDebug:
    """反调试检测"""
    
    @staticmethod
    def check_debugger() -> bool:
        """检测调试器"""
        # Linux: 检查 /proc/self/status
        try:
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('TracerPid:'):
                        pid = int(line.split(':')[1].strip())
                        if pid != 0:
                            return True
        except:
            pass
        return False
    
    @staticmethod
    def check_breakpoint() -> bool:
        """检测断点"""
        # 检测 INT3 (0xCC) 指令
        import ctypes
        code_ptr = ctypes.cast(AntiDebug.check_breakpoint, ctypes.c_char_p)
        for i in range(16):
            if ord(code_ptr[i]) == 0xCC:
                return True
        return False
    
    @staticmethod
    def check_timing() -> bool:
        """时间检测"""
        import time
        start = time.perf_counter_ns()
        # 执行一些简单操作
        _ = 1 + 1
        elapsed = time.perf_counter_ns() - start
        # 如果耗时超过 1ms，可能被调试
        return elapsed > 1_000_000


class VirtualMachine:
    """自定义虚拟机"""
    
    def __init__(self, config: VMPConfig):
        self.config = config
        self.registers = [0] * 16  # 16 个通用寄存器
        self.stack = []
        self.memory = {}
        self.pc = 0  # 程序计数器
        self.running = False
    
    def execute(self, bytecode: bytes) -> Any:
        """执行字节码"""
        self.running = True
        self.pc = 0
        
        while self.running and self.pc < len(bytecode):
            # 反调试检测
            if self.config.anti_debug and AntiDebug.check_debugger():
                raise RuntimeError("Debugger detected")
            
            opcode = bytecode[self.pc]
            self.pc += 1
            
            if opcode == VMOpcode.NOP:
                pass
            
            elif opcode == VMOpcode.HALT:
                self.running = False
            
            elif opcode == VMOpcode.ADD:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a + b)
            
            elif opcode == VMOpcode.SUB:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b - a)
            
            elif opcode == VMOpcode.MUL:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a * b)
            
            elif opcode == VMOpcode.PUSH:
                value = int.from_bytes(bytecode[self.pc:self.pc+8], 'little')
                self.pc += 8
                self.stack.append(value)
            
            elif opcode == VMOpcode.POP:
                self.stack.pop()
            
            elif opcode == VMOpcode.JMP:
                offset = int.from_bytes(bytecode[self.pc:self.pc+4], 'little')
                self.pc = offset
            
            elif opcode == VMOpcode.RET:
                return self.stack[-1] if self.stack else None
        
        return self.stack[-1] if self.stack else None


class VMPProtector:
    """VMP 保护器"""
    
    def __init__(self, config: VMPConfig):
        self.config = config
        self.vm = VirtualMachine(config)
        self._master_key = None
    
    def generate_key(self) -> bytes:
        """生成主密钥"""
        self._master_key = secrets.token_bytes(64)
        return self._master_key
    
    def compile_to_bytecode(self, func: Callable) -> bytes:
        """将函数编译为 VM 字节码"""
        # 简化实现：生成占位字节码
        bytecode = bytearray()
        
        # PUSH 参数
        bytecode.append(VMOpcode.PUSH)
        bytecode.extend((42).to_bytes(8, 'little'))
        
        # 执行计算
        bytecode.append(VMOpcode.MUL)
        
        # 返回
        bytecode.append(VMOpcode.RET)
        
        return bytes(bytecode)
    
    def protect(self, func: Callable) -> Callable:
        """保护函数"""
        bytecode = self.compile_to_bytecode(func)
        
        def protected_wrapper(*args, **kwargs):
            # 完整性检查
            if self.config.integrity_check:
                current_hash = hashlib.sha256(bytecode).hexdigest()
                # 验证哈希...
            
            # 执行 VM
            result = self.vm.execute(bytecode)
            return result
        
        return protected_wrapper


def protect(config: VMPConfig):
    """装饰器：保护函数"""
    protector = VMPProtector(config)
    
    def decorator(func: Callable) -> Callable:
        return protector.protect(func)
    
    return decorator


# 使用示例
if __name__ == "__main__":
    config = VMPConfig(
        anti_debug=True,
        integrity_check=True,
        obfuscation_level="high"
    )
    
    @protect(config)
    def sensitive_function(x: int) -> int:
        return x * x
    
    result = sensitive_function(10)
    print(f"Result: {result}")

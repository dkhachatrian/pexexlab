	.file	"testovf.c"
	.text
	.p2align 4,,15
	.globl	testovf
	.type	testovf, @function
testovf:
.LFB0:
	.cfi_startproc
	movq	big(%rip), %rdx
	movabsq	$9223372036854775807, %rax
	addq	%rdx, %rax
	cmpq	%rax, %rdx
	setg	%al
	ret
	.cfi_endproc
.LFE0:
	.size	testovf, .-testovf
	.globl	big
	.data
	.align 8
	.type	big, @object
	.size	big, 8
big:
	.quad	9223372036854775807
	.ident	"GCC: (GNU) 6.2.0"
	.section	.note.GNU-stack,"",@progbits

我在制作stellaris的mod，我需要你的协助
我当前遇到一个问题，我需要对行星岗位产出进行计算，当前的计算是这样的

```stellaris
bca_base_energy = {
	base = 6
	modifier = {
		add = 2
		owner = { is_robot_empire = yes }
	}
}

cba_planet_energy_job_mult = {
	base = 1
	add = modifier:planet_jobs_produces_mult
	add = modifier:planet_jobs_productive_produces_mult
	add = modifier:planet_jobs_worker_produces_mult

	add = modifier:planet_jobs_energy_produces_mult
	add = modifier:planet_technician_produces_mult
	add = modifier:planet_technician_energy_produces_mult

	add = modifier:planet_jobs_simple_drone_produces_mult
	add = modifier:planet_jobs_complex_and_simple_drone_produces_mult
	modifier = {
		add = modifier:habitat_jobs_produces_mult
		is_planet_class = pc_habitat
	}
}

bca_jobs_for_energy = {
	add = modifier:job_technician_add
	add = modifier:job_technician_drone_add
}

bca_unit_energy_production = {
	add = value:bca_base_energy
	add = modifier:planet_technician_energy_produces_add
	multiply = value:cba_planet_energy_job_mult
}

bca_protential_standard_energy_production = {
	add = value:bca_jobs_for_energy
	divide = 100
	mult = value:bca_unit_energy_production
}
```

当前这个代码只差一个修改就能完美计算出行星的产出了，就是岗位效率的计算

其在本地化文件中是这样描述的
```
 EXPLAIN_WORKFORCE_BONUS: "因为岗位效率增益，该岗位的产出受$BONUS|1G$额外劳动力的提升。"
 EXPLAIN_WORKFORCE_MALUS: "由于岗位效率惩罚（包括行星宜居性等方面），该岗位产能欠佳，相当于以$MALUS|1R$劳动力运转。"
 BONUS_JOB_AMOUNT: "$CURRENT|0G$/$MAX|0$"
 MALUS_JOB_AMOUNT: "$CURRENT|0R$/$MAX|0$"
```
也就是说我代码中的 `bca_jobs_for_energy` 还需要加上一个修正才能还原。我已经进行相关的计算验证确认就是差这一个修正。


我当前已经找到了这个修正叫 `modifier:pop_bonus_workforce_mult` 修正需要这样的计算修改实际的 bca_jobs_for_energy = 原本的 bca_jobs_for_energy * (1+modifier:pop_bonus_workforce_mult)
你能帮我对现有的三个产出计算应用这个修正吗？
因为stellaris的script_value只能做线性计算，所以你需要再定义一个新的script_value来计算script_value，然后在现有的三个产出计算中调用这个新的script_value。
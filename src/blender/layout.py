def m_order(l: int) -> list[int]:
	order = [0]
	for m in range(1, l + 1):
		order.extend([-m, m])
	return order

def group_orbitals(orbitals: dict):
	rows = {}
	basis_order = {"real": 0, "complex": 1}
	keys = sorted(orbitals, key=lambda key: (
		basis_order.get(key[3], 99),
		key[0], key[1], m_order(key[1]).index(key[2])
	))

	for n, l, m, basis in keys:
		obj = orbitals[(n, l, m, basis)]
		rows.setdefault(basis, {}).setdefault(n, {}).setdefault(l, []).append(obj)
	return rows

def arrange_orbital_grid(rows, margin_x=8, margin_y=30, margin_l=18, margin_basis=30, x_offset = 0):
	max_right = x_offset
	basis_offset = x_offset
	for basis, groups_n in rows.items():
		y_cursor = 0

		for n, groups_l in groups_n.items():
			x_cursor = basis_offset	
			row_height = 0

			for l, objs in groups_l.items():
				for obj in objs:
					width = obj.dimensions.x
					height = obj.dimensions.y

					obj.location.x = x_cursor + width / 2
					obj.location.y = y_cursor
					obj.location.z = 0

					x_cursor += width + margin_x
					row_height = max(row_height, height)

					max_right = max(max_right, obj.location.x + width / 2)

				# espaço extra entre blocos de l
				x_cursor += margin_l

			y_cursor -= row_height + margin_y

		basis_offset = max_right + margin_basis

	return max_right
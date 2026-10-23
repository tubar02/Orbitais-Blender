def m_order(l: int) -> list[int]:
	order = [0]
	for m in range(1, l + 1):
		order.extend([-m, m])
	return order

def group_orbitals(orbitals: dict):
	rows = {}
	keys = sorted(orbitals, key=lambda key: (
		key[0], key[1], m_order(key[1]).index(key[2]), key[3]
	))

	for n, l, m, basis in keys:
		obj = orbitals[(n, l, m, basis)]
		rows.setdefault(n, {}).setdefault(l, []).append(obj)
	return rows

def arrange_orbital_grid(rows, margin_x=8, margin_y=30, margin_l=18):
	y_cursor = 0

	for n, groups_l in rows.items():
		x_cursor = 0
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

			# espaço extra entre blocos de l
			x_cursor += margin_l

		y_cursor -= row_height + margin_y
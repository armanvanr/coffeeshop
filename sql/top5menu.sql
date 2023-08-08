SELECT * FROM public.user
ORDER BY id

SELECT * FROM public.menu
ORDER BY category, id

SELECT SUM(o_items.quantity), o_items.menu_id
FROM order_items AS o_items
JOIN public.order AS o
ON o.id = o_items.order_id
-- JOIN menu AS m
-- ON m.id = o_items.menu_id
WHERE o.status = 'completed'
GROUP BY o_items.menu_id
ORDER BY SUM(o_items.quantity) DESC

SELECT * FROM public.order ORDER BY id;
SELECT * FROM public.order_items;

SELECT SUM(oi.quantity) total_qty_ordered, oi.menu_id, oi.menu_name, menu.desc
FROM order_items oi JOIN
public.order o ON oi.order_id = o.id
JOIN menu ON menu.id = oi.menu_id
WHERE o.status = 'completed' AND menu.category = 'drinks'
GROUP BY oi.menu_id, oi.menu_name, menu.desc
ORDER BY total_qty_ordered DESC
LIMIT 5

SELECT *
FROM public.order
WHERE status='completed';
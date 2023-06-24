SELECT *
FROM public.balance_record
WHERE member_name IS null
ORDER BY user_id

UPDATE public.balance_record
-- SET member_name = 'Asri' WHERE user_id = 5
-- SET member_name = 'Vian' WHERE user_id = 6
-- SET member_name = 'Ridwan' WHERE user_id = 7
-- SET member_name = 'Andro' WHERE user_id = 8
-- SET member_name = 'Rafi' WHERE user_id = 9
-- SET member_name = 'Sela' WHERE user_id = 10

SELECT *
FROM public.user
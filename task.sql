-- Output the number of movies in each category, sorted descending.

SELECT c.name AS category, COUNT(*) AS films_count
FROM film_category fc
JOIN category c USING (category_id)
GROUP BY c.name
ORDER BY films_count DESC;


-- Output the 10 actors whose movies rented the most, sorted in descending order.

SELECT 
    a.actor_id,
    a.first_name || ' ' || a.last_name AS actor_name,
    COUNT(r.rental_id) AS total_rentals
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN inventory i ON fa.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY total_rentals DESC
LIMIT 10;

-- Output the category of movies on which the most money was spent.

SELECT 
    c.name AS category,
    ROUND(SUM(p.amount)::numeric, 2) AS total_revenue
FROM category c
JOIN film_category fc USING (category_id)
JOIN film f USING (film_id)
JOIN inventory i USING (film_id)
JOIN rental r USING (inventory_id)
JOIN payment p USING (rental_id)
GROUP BY c.category_id, c.name
ORDER BY total_revenue DESC
LIMIT 1;

--Print the names of movies that are not in the inventory. Write a query without using the IN operator.

SELECT f.title
FROM film f
LEFT JOIN inventory i USING (film_id)
WHERE i.inventory_id IS NULL
ORDER BY f.title;

-- Output the top 3 actors who have appeared the most in movies in the “Children” category. If several actors have the same number of movies, output all of them.

WITH children_stats AS (
    SELECT 
        a.actor_id,
        a.first_name || ' ' || a.last_name AS actor,
        COUNT(*) AS films_in_children
    FROM actor a
    JOIN film_actor fa USING (actor_id)
    JOIN film_category fc USING (film_id)
    JOIN category c USING (category_id)
    WHERE c.name = 'Children'
    GROUP BY a.actor_id, a.first_name, a.last_name
),
ranked AS (
    SELECT 
        actor,
        films_in_children,
        RANK() OVER (ORDER BY films_in_children DESC) AS rnk
    FROM children_stats
)
SELECT actor, films_in_children
FROM ranked
WHERE rnk <= 3
ORDER BY films_in_children DESC, actor;

-- Output cities with the number of active and inactive customers (active - customer.active = 1). Sort by the number of inactive customers in descending order.

SELECT 
    ci.city,
    COUNT(*) FILTER (WHERE cu.active = 1) AS active_customers,
    COUNT(*) FILTER (WHERE cu.active = 0) AS inactive_customers
FROM city ci
JOIN address a USING (city_id)
JOIN customer cu USING (address_id)
GROUP BY ci.city_id, ci.city
ORDER BY inactive_customers DESC, ci.city;

-- Output the category of movies that have the highest number of total rental hours in the city (customer.address_id in this city)
-- and that start with the letter “a”. Do the same for cities that have a “-” in them. Write everything in one query.

WITH rental_hours AS (
    SELECT
        ci.city,
        c.name AS category,
        -- Считаем часы только для завершённых прокатов
        SUM(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600.0) AS total_hours
    FROM rental r
    JOIN customer cu ON r.customer_id = cu.customer_id
    JOIN address a ON cu.address_id = a.address_id
    JOIN city ci ON a.city_id = ci.city_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE r.return_date IS NOT NULL  -- только завершённые аренды
    GROUP BY ci.city, c.name
),
grouped AS (
    SELECT
        city,
        category,
        total_hours,
        -- Определяем группу города
        CASE 
            WHEN city ILIKE 'a%' THEN 'starts_with_a'
            WHEN city LIKE '%-%' THEN 'contains_dash'
        END AS city_group
    FROM rental_hours
    WHERE city ILIKE 'a%' OR city LIKE '%-%'
),
ranked AS (
    SELECT
        city_group,
        category,
        ROUND(SUM(total_hours)::numeric, 2) AS total_hours,
        ROW_NUMBER() OVER (PARTITION BY city_group ORDER BY SUM(total_hours) DESC) AS rn
    FROM grouped
    WHERE city_group IS NOT NULL
    GROUP BY city_group, category
)
SELECT 
    CASE 
        WHEN city_group = 'starts_with_a' THEN 'Cities starting with "a"'
        WHEN city_group = 'contains_dash' THEN 'Cities containing "-"'
    END AS description,
    category,
    total_hours
FROM ranked
WHERE rn = 1
ORDER BY description;


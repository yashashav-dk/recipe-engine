# Recipe Engine — Guidelines

## Indian Cooking Principles

These principles are non-negotiable when creating, reviewing, or modifying any recipe. They come from traditional Indian cooking wisdom validated by food science.

### Building a Curry Base

1. **Bloom spices in fat, never add to liquid.** Fat-soluble flavor compounds only fully extract in hot oil/ghee. 30-45 seconds of blooming in oil transforms raw/chalky spice into rich/rounded flavor. Adding ground spices directly to watery sauce wastes them.

2. **Brown onions properly — 15-25 minutes, not 5.** The Maillard reaction creates hundreds of flavor compounds that don't exist in raw onions. If you think onions are done, they're probably halfway. Golden-brown = color of caramel, not straw. A pinch of salt early draws moisture and speeds browning.

3. **Cook the masala until oil separates.** Oil pooling at edges/surface means: all moisture evaporated, spices fully cooked (no raw taste), flavors concentrated and melded. If oil hasn't separated, the base isn't done.

4. **Use less tomato than you think.** Onion-to-tomato ratio should be at least 2:1 by weight for North Indian gravies. Too much tomato dilutes spice intensity and makes curry one-dimensional and acidic. Tomato is a supporting ingredient, not the star.

### Seasoning

5. **Salt at every stage, taste at every stage.** Indian cooking seasons at minimum 3-4 points:
   - With onions (draws moisture, speeds browning)
   - With spice paste (integrates with fat-soluble compounds)
   - With protein (begins penetrating)
   - Final adjustment (corrects for concentration)
   Never dump all salt in at once. Never skip tasting before finishing.

6. **Target 1-1.5% salt by total food weight** (10-15g per kg). Under-salting is the #1 reason home curry doesn't taste like restaurant food. If it tastes "flat" or "missing something," it needs salt, not more spice.

7. **For meal prep, season 10-15% more than tastes perfect.** Cold food tastes less salty. Reheating doesn't fully restore flavor. Starch and protein absorb seasoning over days. Slight "over-seasoning" when hot = perfectly seasoned when reheated from cold.

### Spice Layering

8. **Layer spices at three stages:**
   - **Oil layer (start):** Whole spices in hot oil — background aromatics
   - **Paste layer (middle):** Ground spices bloomed into onion-tomato paste — body and heat
   - **Finishing layer (end):** Garam masala, kasuri methi, fresh herbs — bright top notes
   Never add all garam masala at the beginning. Reserve at least half for the last 2-3 minutes.

9. **Liquid dilutes spice intensity.** Build a concentrated, oil-separated spice paste BEFORE adding any liquid. Adding liquid too early means you need dramatically more spice for the same result, and the flavor is never as clean.

### Pressure Cooking (Instant Pot)

10. **Fully develop the base on saute BEFORE sealing the lid.** Under pressure there's no Maillard reaction, no caramelization, no blooming. The pressure phase only tenderizes protein and melds existing flavors — it cannot create flavor that isn't already there.

11. **Pressure cooking dilutes, not concentrates.** It traps all steam (opposite of stovetop reduction). Use more spices and more seasoning than you would for stovetop cooking.

12. **Always finish on saute after pressure.** Reduces excess liquid, lets you add finishing spices (garam masala, kasuri methi) that would lose volatiles under pressure, and lets you taste and adjust.

13. **Chicken breast: 5 mins pressure, quick release.** Exceeding this makes breast rubbery. Thighs are more forgiving (5-7 mins) and preferred for curry — more fat, more flavor, harder to overcook.

### Batch Cooking / Meal Prep

14. **Curry genuinely tastes better on day 2-3.** Flavor molecules continue diffusing, harsh spice notes mellow, different elements combine into a more unified taste. This is a feature, not a bug.

15. **Gravies thicken when cooled — plan for it.** Add a splash of water when reheating. This is normal and indicates a well-made, properly reduced gravy.

16. **Refresh when reheating.** Squeeze of lemon, pinch of garam masala, or fresh cilantro after reheating restores brightness that storage dulls.

### Tikka Masala Specifically

17. **Without char, it's butter chicken, not tikka masala.** The yogurt-marinated chicken must be seared/charred at high heat. The charred yogurt coating creates unique Maillard compounds that define tikka masala.

18. **Kasuri methi is the secret ingredient.** Crushed and added in the final minutes — provides a slightly sweet, nutty, almost maple-like note that is the hallmark of restaurant tikka masala.

19. **A pinch of sugar balances tomato acidity.** 0.5-1 tsp in the whole pot rounds the flavor and eliminates the sharp/sour edge from tomato.

### Diagnostic Cheat Sheet

| Problem | Fix |
|---------|-----|
| Tastes flat | Add salt |
| One-dimensional | Add acid (lemon juice) |
| Lacks aroma | Add finishing spices (garam masala, kasuri methi) |
| Too tomatoey | Too much tomato or not cooked down enough; add cream/yogurt or sugar |
| Too spicy (heat) | Add yogurt, cream, or sugar |
| Watery/thin | Simmer on saute to reduce |
| Chalky spice taste | Spices weren't bloomed in fat; cook longer on saute |

## Recipe Workflow

- Always generate both YAML and docs: `python3 scripts/generate.py`
- When modifying recipes, regenerate and push so the website stays in sync
- Recipe YAML is source of truth; markdown and HTML are generated artifacts

## When Reviewing or Creating Recipes

- Check that the recipe seasons the gravy base independently from any marinade
- Verify salt is added at multiple stages in the steps, not just once
- Confirm ground spices are bloomed in oil before liquid is added
- Check onion-to-tomato ratio (should be >= 2:1 by weight)
- For meal prep recipes, ensure seasoning accounts for flavor loss during storage
- Flag any recipe that adds all spices to a marinade and none to the base

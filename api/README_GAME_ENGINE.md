# Exquisite Exoplanets - Game Engine

## Game Config

Below are the config templates in order to create items for the game. These configs are created in `YAML`. An example is
also given.

> ![NOTE] Cannot include `inf`.

### Planet Template

Structure:

```yaml
PLANET_ID:
  name: 'ResourceName'
  tier: [0, inf)
  description: 'ResourceDescription'
```

Example:

```yaml
EA0000:
  name: 'Earth'
  tier: 0
  description: 'This empty husk used to be the most magnificent green world, believe it or not'
```

### Resource Template

Structure:

```yaml
RESOURCE_ID:
    name: 'ResourceName'
    min_tier: [0, inf) # minimal tier at which the resource can appear
    unit_price: [0, inf) # unit price by cubic meter
    unit_xp: [0, inf) # xp obtained for each unit harvested

    # probability of making the resource appear on a planet, scaling with planet tier
    # actual probability = init_probability * upscale^tier
    apparition_probability: [0,1]
    tier_apparition_upscale: [1,inf)

    # average amount of units by planet
    # actual units = normal probability centered on [init_units * upscale^tier]
    init_units: [0,1]
    tier_units_upscale: [1,inf)

    # the rate at which the units decrease each time the resource is collected
    # options
    #   - linear : a fixed amount is removed each time
    #     linear factor : [0, inf[
    #   - exponential : the amount removed scales down with the density (density(t)=init_density*exp(-t/factor))
    #     exponential factor : 5*factor is the number of epochs to collect 99% resources
    #   - geometric : the density is multiplied by a factor < 1 each time
    #     geometric factor : [0, 1]
    decay_function: 'linear'
    decay_factor: [0, inf)  # depends on the decay function
    balancing_delay: 1 # number of units/s  #this is the expected average units/s overall
```

Example:

```yaml
WA00:
  name: water
  min_tier: 0
  unit_price: 3.0
  unit_xp: 0.03
  init_units: 100000
  tier_units_upscale: 10
  decay_function: 'exponential'
  decay_factor: 75.0
  balancing_delay: 0.09259259259
```

### Resource Collector Template

Structure:

```yaml
RESOURCE_COLLECTOR_ID:
  name: 'ResourceCollectorName'
  tier: 1
  init_price: [0, inf)  # buying price
  init_speed: [0, inf)  # resource harvest speed

  upgrade_upscale: [1, inf)  # multiplication of speed for each tier
  upgrade_init_price: [0, inf)  # first upgrade price
  upgrade_price_upscale: [1, inf)  # multiplication of price by tier
  cost_of_use: [0, inf)  # how much money do you need to operate the machine / epoch
  cost_of_use_price_upscale : [1, inf)  # the multiplication of the cost to use per tier
  resources:  # the resources this collector can cover with the respective minimal tier upgrade needed
    WO00 : 0
    IR00 : 1
```

Example:

```yaml
FO00:
  name: foundry
  tier: 1
  init_price: 10000
  init_speed: 1
  upgrade_upscale: 7
  upgrade_init_price: 250000
  upgrade_price_upscale: 10
  cost_of_use: 10
  cost_of_use_price_upscale : 2
  resources:
    IR00: 1
    AL00: 2
    LE00: 2
    ZI00: 2
```

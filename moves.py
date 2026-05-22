#Moves
class Move: #Makes moves more organized and readable
  def __init__(self, name, damage, cooldown, ce_cost, crit = 1.5, is_domain =False, can_dodge = True, burn = False, freeze = False, blood = False, heal = False, soul_resistence = False):
    self.name = name
    self.damage = damage
    self.cooldown= cooldown
    self.ce_cost = ce_cost
    self.crit = crit
    self.is_domain = is_domain
    self.can_dodge = can_dodge
    self.burn = burn
    self.freeze = freeze
    self.blood = blood
    self.heal = heal
    self.soul_resistence = soul_resistence


## Definitions of target qualities

- ``f_rho:`` the distance quality factor for that camera-target pair
- ``f_theta:`` how obliquely the camera hits the target. Straight-on is good, glancing is bad
- ``weight:`` Calculated using f_rho and f_theta. A number between 0 and 1 saying how useful one camera is for one target
(weight_factors).
- ``sector_8 & sector_4:``  A sector (directional bin). The compass around a target's normal, divided into equal wedges: 8 by default. Every observing camera falls in exactly one wedge (sector_indicies). Cameras in deffierent sectors see the targets from different directions. I think sectores are from [0,7]
- ``best:`` a boolean. The single winner of a sector. If 3 cameras in sector 5, the one with the highest weight gets best = True. See _check_best in loaders.py
- ``diversity:`` how spread out the good views are. A target seen by 6 cameras in one sector has bad diversity. Sectors are imprtant for anaylising how much info you have on a target
- ```score:``` targets overall coverage quality. I think [0,1]
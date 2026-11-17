---
title: "MATPOWER "
url: https://pandapower.readthedocs.io/en/v3.2.1/converter/matpower.html
published: 
fetched: 2026-11-17
type: docs
topics: [tools-execution, pandapower, conversion, identity]
summary: "MATPOWER 文件与 ppc 字典入口、0/1 起点和频率参数，支持转换语义审计。"
---

# MATPOWER 

To communicate to MATPOWER to exchange network data these functions are available.

pandapower.converter.from_mpc(*mpc_file*, *f_hz=50*, *casename_mpc_file='mpc'*, *validate_conversion=False*, ***kwargs*)[](https://pandapower.readthedocs.io/en/v3.2.1/converter/matpower.html#pandapower.converter.from_mpc "Link to this definition")
:   This function converts a matpower case file version 2 to a pandapower net.

    Note: If ‘mpc_file’ ends with ‘.m’ the python package ‘matpowercaseframes’ is used. If
    ‘mpc_file’ ends with ‘.mat’ ‘scipy.io.loadmat’ is used. Other file endings are not supported.
    In that other cases, please, rename the file ending or use the internal subfunctions.

    Note: python is 0-based while Matlab is 1-based.

    INPUT:

    > **mpc_file** - path to a matpower case file (.mat format not .m script).

    OPTIONAL:

    > **f_hz** (int, 50) - The frequency of the network.
    >
    > **casename_mpc_file** (str, ‘mpc’) - The name of the variable in .mat file which contain
    > the matpower case structure, i.e. the arrays “gen”, “branch” and “bus”.
    >
    > ****kwargs** - key word arguments for from_ppc()

    OUTPUT:

    > **net** - The pandapower network

    EXAMPLE:
    :   ```
        >>> from pandapower.converter import from_mpc
        >>>
        >>> pp_net1 = from_mpc('case9.mat', f_hz=60)
        >>> pp_net2 = from_mpc('case9.m', f_hz=60)
        ```

pandapower.converter.to_mpc(*net*, *filename=None*, ***kwargs*)[](https://pandapower.readthedocs.io/en/v3.2.1/converter/matpower.html#pandapower.converter.to_mpc "Link to this definition")
:   This function converts a pandapower net to a matpower case files (.mat) version 2.
    Note: python is 0-based while Matlab is 1-based.

    INPUT:
    :   **net** - The pandapower net.

    OPTIONAL:
    :   **filename** (str, None) - File path + name of the mat file which will be created. If None
        :   the mpc will only be returned

        ****kwargs** - please look at to_ppc() documentation

    EXAMPLE:
    :   ```
        >>> from pandapower.converter import to_mpc
        >>> from pandapower.networks.power_system_test_cases import case9
        >>>
        >>> net = case9()
        >>> to_mpc(net, "case9.mat")
        ```

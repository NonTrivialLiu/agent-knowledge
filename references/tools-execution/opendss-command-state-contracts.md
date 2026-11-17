---
title: "OpenDSS Documentation"
url: https://opendss.epri.com/Executive2.html
published: 
fetched: 2026-11-17
type: docs
topics: [tools-execution, opendss, commands, state]
summary: "Compile、Redirect 与控制命令涉及目录、活动电路和控制生命周期，支持领域命令审计。"
---

# OpenDSS Documentation

1. [Basics of the OpenDSS Scripting Language](https://opendss.epri.com/BasicsoftheOpenDSSScriptingLangu.html)
2. [Basics Commands](https://opendss.epri.com/BasicsCommands.html)

## Executive

The following properties are part of the command executive 

|  |  |
| --- | --- |
| // | Comment.  Command line is ignored. |
| ? | Inquiry for property value.  Result is put into GlobalReault and can be seen in the Result Window. Specify the full property name.    Example: ? Line.Line1.R1    Note you can set this property merely by saying:    Line.line1.r1=.058 |
| _DoControlActions | For step control of solution process: Pops control actions off the control queue according to the present control mode rules. Dispatches contol actions to proper control element "DoPendingAction" handlers. |
| _InitSnap | For step control of solution process: Intialize iteration counters, etc. that normally occurs at the start of a snapshot solution process. |
| _SampleControls | For step control of solution process: Sample the control elements, which push control action requests onto the control queue. |
| _ShowControlQueue | For step control of solution process: Show the present control queue contents |
| _SolveDirect | For step control of solution process: Invoke direct solution function in DSS. Non-iterative solution of Y matrix and active sources only. |
| _SolveNoControl | For step control of solution process: Solves the circuit in present state but does not check for control actions. |
| _SolvePFlow | For step control of solution process: Invoke iterative power flow solution function of DSS directly. |
| ~ | Continuation of editing on the active object. An abbreviation.    Example:    New Line.Line1 Bus1=aaa  bus2=bbb  ~ R1=.058  ~ X1=.1121 |
| Abort | Aborts all the simulations running |
| About | Display "About Box".  (Result string set to Version string.) |
| AddBusMarker | Add a marker to a bus in a circuit plot. Markers must be added before issuing the Plot command. Effect is persistent until circuit is cleared. See also ClearBusMarkers command. Example:     ClearBusMarkers    !...Clears any previous bus markers  AddBusMarker Bus=Mybusname code=5 color=Red size=3    You can use any of the standard color names  or RGB numbers. See Help on C1 property in Plot command. |
| AggregateProfiles | Aggregates the load shapes in the model using the number of zones given in the argument.  Use this command when the number of load shapes is considerably big, this algorithm will simplify  the amount of load shapes in order to make the memory consumption lower for the model.  The output of this algorithm is a script describing the new load shapes and their application into loads across the model.    The argument on this command can be: Actual/pu to define the units in which the load profiles are.  Check the OpenDSS user manual for details |
| AlinfFile | Alignfile [file=]filename.  Aligns DSS script files in columns for easier reading. |
| AllocateLoads | Estimates the allocation factors for loads that are defined using the XFKVA property. Requires that energymeter objects be defined with the PEAKCURRENT property set. Loads that are not in the zone of an energymeter cannot be allocated. |
| AllPCEatBus | Brings back the names of all PCE connected to the bus specified in the argument.  The command goes as follows:    AllPCEatBus myBus    Where "myBus" is the name of the bus of interest |
| AllPDatBus | Brings back the names of all PDE connected to the bus specified in the argument.  The command goes as follows:    AllPDEatBus myBus    Where "myBus" is the name of the bus of interest |
| BatchEdit | Batch edit objects in the same class. Example: BatchEdit Load..* duty=duty_shape  In place of the object name, supply a PERL regular expression. .* matches all names.  The subsequent parameter string is applied to each object selected. |
| BuildY | Forces rebuild of Y matrix upon next Solve command regardless of need. The usual reason for doing this would be to reset the matrix for another load level when using LoadModel=PowerFlow (the default) when the system is difficult to solve when the load is far from its base value.  Works by invalidating the Y primitive matrices for all the Power Conversion elements. |
| Buscoords | Define x,y coordinates for buses.  Execute after Solve or MakeBusList command is executed so that bus lists are defined.Reads coordinates from a CSV file with records of the form: busname, x, y.    Example: BusCoords [file=]xxxx.csv |
| CalcIncMatrix | Calculates the incidence matrix of the Active Circuit |
| CalcIncMatrix_O | Calculates the incidence matrix of the Active Circuit. However, in this case the matrix will be calculated considering its hierarchical order,listing the buses starting from the substation to the farthest load in the model |
| CalcLaplacian | Calculate the laplacian matrix using the incidence matrix previously calculated. Before calling this command the incidence matrix needs to be calculated using calcincmatrix/calcincmatrix_o. |
| Calcvoltagesbases | Calculates voltagebase for buses based on voltage bases defined with Set voltagebases=... command. |
| Capacity | Find the maximum load the active circuit can serve in the PRESENT YEAR. Uses the EnergyMeter objects with the registers set with the SET UEREGS= (..) command for the AutoAdd functions.  Syntax (defaults shown):    capacity [start=]0.9 [increment=]0.005    Returns the metered kW (load + losses - generation) and per unit load multiplier for the loading level at which something in the system reports an overload or undervoltage. If no violations, then it returns the metered kW for peak load for the year (1.0 multiplier). Aborts and returns 0 if no energymeters. |
| CD | Change default directory to specified directory    CD dirname |
| Check4Updates | Returns a message indicating if there is a new version of OpenDSS avaialble for download. Requires internet connection. |
| Cktlosses | Returns the total losses for the active circuit in the Result string in kW, kvar. |
| Classes | List of intrinsic DSS Classes. Returns comma-separated list in Result variable. |
| Cleanup | Force execution of the end-of-time-step cleanup functions that samples/saves meters and updates selected state variables such as storage level |
| Clear | Clear all circuits currently in memory. |
| ClearAll | Clears all the circuits and all the actors, after this instruction there will be only 1 actor (actor 1) and will be the active actor |
| ClearBusMarkers | Clear all bus markers created with the AddBusMarker command. |
| Clone | Clones the active circuit. This command creates as many copies of the active cirucit as indicated in the argument if the number of requested clones does not overpasses the number of local CPUs. The form of this command is clone X whereX is the number of clones to be created |
| Close | Opposite of the Open command. |
| CloseDI | Close all DI files ... useful at end of yearly solution where DI files are left open. (Reset and Set Year=nnn will also close the DI files) |
| COMHelp | Shows the documentation file for the COM interface.This file provides guidance on the properties and methods included in the COM interface as well as examples and tips. Use this file to learn more about the COM interface and its different interfaces or just as a reference guide. |
| Comparecases | [Case1=]casename [case2=]casename [register=](register number) [meter=]{Totals* | SystemMeter | metername}.   Compares yearly simulations of two specified cases with respect to the quantity in the designated register from the designated meter file. Defaults: Register=9 meter=Totals.  Example:    Comparecases base pvgens 10 |
| Compile | Reads the designated file name containing DSS commands and processes them as if they were entered directly into the command line. The file is said to be "compiled." Similar to "redirect" except changes the default directory to the path of the specified file.    Syntax:    Compile filename |
| Connect | Request to create a TCP/IP socket to communicate data with external modules. This function requires the host address and TCP port to connect. |
| Currents | Returns the currents for each conductor of ALL terminals of the active circuit element in the Result string. (See Select command.)Returned as comma-separated magnitude and angle. |
| CvrtLoadShapes | Convert all Loadshapes presently loaded into either files of single or files of double. Usually files of singles are adequate precision for loadshapes.  Syntax:    cvrtloadshapes type=sng  (this is the default)  cvrtloadshapes type=dbl    A DSS script for loading the loadshapes from the created files is produced and displayed in the default editor. |
| DDLLHelp | Shows the documentation file for the Direct DLL shared library.This file provides guidance on the interfaces included in the DirectDLL shared library. Use this file to learn more about the DirectDLL and its different interfaces or just as a reference guide. |
| DI_plot | [case=]casename [year=]yr [registers=](reg1, reg2,...)  [peak=]y/n  [meter=]metername  Plots demand interval (DI) results from yearly simulation cases.  Plots selected registers from selected meter file (default = DI_Totals.CSV).  Peak defaults to NO.  If YES, only daily peak of specified registers is plotted. Example:     DI_Plot basecase year=5 registers=(9,11) no |
| Disable | Disables a circuit element or entire class.  Example:    Disable load.loadxxx  Disable generator.*  (Disables all generators)    The item remains defined, but is not included in the solution. |
| Disconnect | Request to terminate a TCP/IP socket. This function requires the host address and TCP port to disconnect. |
| Distribute | kw=nn how={Proportional* | Uniform |Random | Skip} skip=nn PF=nn file=filename MW=nn What=[Generator*|Load]    Creates a DSS script file to distribute Generator or Load objects on the system in the manner specified by "how".  kW = total generation to be distributed (default=1000)   how= process name as indicated (default=proportional to load)  skip = no. of buses to skip for "How=Skip" (default=1)  PF = power factor for new generators (default=1.0)  file = name of file to save (default=distgenerators.dss or distloads.dss)  MW = alternate way to specify kW (default = 1)  What = what type of device to add, Generator (default) or Load |
| DOScmd | Do a DOS command. Sends the command "cmd ... " to Windows. Execute the "cmd /?" command in a DOS window to see the options. To do a DOS command and automatically exit, do     DOScmd /c ...command string ...    To keep the DOS window open, use /k switch. |
| Dump | Display the properties of either a specific DSS object or a complete dump on all variables in the problem (Warning! Could be very large!). Brings up the default text editor with the text file written by this command.   Syntax: dump [class.obj] [debug]   Examples:     Dump line.line1    Dump solution  (dumps all solution vars)    Dump commands  (dumps all commands to a text file)    Dump transformer.*  (dumps all transformers)   Dump ALLOCationfactors  (load allocation factors)   Dump Buslist    (bus name hash list)   Dump Devicelist    (Device name hash list)   Dump      (dumps all objects in circuit) |
| Edit | Edit an object. The object is selected and it then becomes the active object.    Note that Edit is the default command.  You many change a property value simply by giving the full property name and the new value, for example:    line.line1.r1=.04  vsource.source.kvll=230 |
| Enable | Enables a circuit element or entire class.  Example:  Enable load.loadxxx  Enable generator.*  (enables all generators) |
| Estimate | Execute state estimator on present circuit given present sensor values. |
| Export | Export various solution values to CSV (or XML) files for import into other programs. Creates a new file except for Energymeter and Generator objects, for which the results for each device of this class are APPENDED to the CSV File. You may export to a specific file by specifying the file name as the LAST parameter on the line. For example:      Export Voltage Myvoltagefile.CSV    Otherwise, the default file names shown in the Export help are used. For Energymeter and Generator, specifying the switch "/multiple" (or /m) for the file name will cause a separate file to be written for each meter or generator. The default is for a single file containing all elements.    May be abreviated Export V, Export C, etc.  Default is "V" for voltages. If Set ShowExport=Yes, the output file will be automatically displayed in the default editor. Otherwise, you must open the file separately. The name appears in the Result window. |
| ExportOverloads | Exports the overloads report with the content avaiable at the moment of the call. It only affects the overloads report for the active actor. |
| ExportVViolations | Exports the voltage violations1 report with the content avaiable at the moment of the call. It only affects the voltage violations report for the active actor. |
| Fileedit | Edit specified file in default text file editor (see Set Editor= option).    Fileedit EXP_METERS.CSV (brings up the meters export file)    "FileEdit" may be abbreviated to a unique character string. |
| FinishTimeStep | Do Cleanup, sample monitors, and increment time. |
| FNCSPublish | Read FNCS publication topics from a JSON file |
| Formedit | FormEdit [class.object].  Brings up form editor on active DSS object. |
| Get | Returns DSS property values set using the Set command. Result is returne in Result property of the Text interface.     VBA Example:    DSSText.Command = "Get mode"  Answer = DSSText.Result    Multiple properties may be requested on one get.  The results are appended and the individual values separated by commas.    See help on Set command for property names. |
| GIS | Executes GIS options working with OpenDSS-GIS. See GIS command help. |
| GISCoords | Define x,y coordinates for buses using real GIS Latitude and Longitude values (decimal numbers).  Similar to BusCoords command. Execute after Solve command or MakeBusList command is executed so that bus lists are defined.Reads coordinates from a CSV file with records of the form: busname, Latitude, Longitude.    Example: GISCoords [file=]xxxx.csv    Note: For using only if OpenDSS-GIS is locally installed. |
| HELICSPublish | Read HELICS publication topics from a JSON file |
| Help | Gives this display. |
| Init | This command forces reinitialization of the solution for the next Solve command. To minimize iterations, most solutions start with the previous solution unless there has been a circuit change.  However, if the previous solution is bad, it may be necessary to re-initialize.  In most cases, a re-initiallization results in a zero-load power flow solution with only the series power delivery elements considered. |
| Interpolate | {All | MeterName}  Default is "All". Interpolates coordinates for missing bus coordinates in meter zone |
| LatLongCoords | Define x,y coordinates for buses using Latitude and Longitude values (decimal numbers).  Similar to BusCoords command. Execute after Solve command or MakeBusList command is executed so that bus lists are defined.Reads coordinates from a CSV file with records of the form: busname, Latitude, Longitude.    Example: LatLongCoords [file=]xxxx.csv    Note: Longitude is mapped to x coordinate and Latitude is mapped to y coordinate. |
| Losses | Returns the total losses for the active circuit element (see Select command) in the Result string in kW, kvar. |
| M | Continuation of editing on the active object. An abbreviation for More |
| MakeBusList | Updates the buslist, if needed, using the currently enabled circuit elements.  (This happens automatically for Solve command.) See ReprocessBuses |
| MakePosSeq | Attempts to convert present circuit model to a positive sequence equivalent. It is recommended to Save the circuit after this and edit the saved version to correct possible misinterpretations. |
| More | Continuation of editing on the active object. |
| New | Create a new object within the DSS. Object becomes the active object  Example: New Line.line1 ... |
| NewActor | This command creates a new actor (OpenDSS Instance) and sets the new actor as the active actor. There can be only 1 circuit per actor. The NewActor command will increment the variable NumOfActors; however, if the number of actors is the same as the number of available CPUs the new actor will not be created generating an error message. This instruction will deliver the ID of the active actor. This command does not requires a precedent command. |
| Next | {Year | Hour | t}  Increments year, hour, or time as specified.  If "t" is specified, then increments time by current step size. |
| NodeDiff | Global result is set to voltage difference, volts and degrees, (Node1 - Node2) between any two nodes. Syntax:       NodeDiff Node1=MyBus.1 Node2=MyOtherBus.1 |
| NodeList | [Circuit element name] (Optional) Returns a list of node numbers for all conductors of all terminals of the active circuit element in the Result window or interface.If the optional circuit element name is supplied, the program makes it the active element. Usage:    NodeList  NodeList Line.Myline |
| Obfuscate | Change Bus and circuit element names to generic values to remove identifying names. Generally, you will follow this command immediately by a "Save Circuit Dir=MyDirName" command. |
| Open | Opens the specified terminal and conductor of the specified circuit element. If the conductor is not specified, all phase conductors of the terminal are opened.    Examples:  Open line.line1 2   (opens all phases of terminal 2)    Open line.line1 2 3  (opens the 3rd conductor of terminal 2) |
| Panel | Displays main control panel window. |
| Phaselosses | Returns the losses for the active circuit element (see Select command) for each PHASE in the Result string in comma-separated kW, kvar pairs. |
| Plot | Plots circuits and results in a variety of manners.  See separate Plot command help. |
| Powers | Returns the powers (complex) going into each conductors of ALL terminals of the active circuit element in the Result string. (See Select command.)Returned as comma-separated kW and kvar. |
| Pstcalc | Pst calculation. PstCalc Npts=nnn Voltages=[array] dt=nnn freq=nn lamp=120 or 230.  Set Npts to a big enough value to hold the incoming voltage array.   dt = time increment in seconds. default is 1  freq = base frequency in Hz 50 or 60. Default is default base frequency  Lamp= 120 for North America; 230 for Europe. Default is 120    PSTCalc Npts=1900 V=[file=MyCSVFile.CSV, Col=3, Header=y] dt=1 freq=60 lamp=120 |
| puvoltages | Just like the Voltages command, except the voltages are in per unit if the kVbase at the bus is defined. |
| Quit | Shuts down DSS unless this is the DLL version.  Then it does nothing;  DLL parent is responsible for shutting down the DLL. |
| Reconductor | Reconductor a line section. Must be in an EnergyMeter zone.   Syntax: Reconductor Line1=... Line2=... {LineCode= | Geometry = } EditString="..." NPhases=#  Line1 and Line2 may be given in any order. All lines in the path between the two are redefined with either the LineCode or Geometry (not both). You may also add an optional string the alter any other line properties. The edit string should be enclosed in quotes or parens or brackets.  Nphases is an optional filter on the number of phases in line segments to change. |
| Redirect | Reads the designated file name containing DSS commands and processes them as if they were entered directly into the command line. Similar to "Compile", but leaves current directory where it was when Redirect command is invoked.Can temporarily change to subdirectories if nested Redirect commands require.    ex:  redirect filename |
| Reduce | {All | MeterName}  Default is "All".  Reduce the circuit according to reduction options. See "Set ReduceOptions" and "Set Keeplist" options.Energymeter objects actually perform the reduction.  "All" causes all meters to reduce their zones. |
| Refine_BusLevels | This function takes the bus levels array and traces all the possible paths considering the longest paths from the substation to the farthest branches within the circuit. Then, the new paths are filled with 0 to complement the oroginal levels proposed by the calcincmatrix_o command. |
| RelCalc | [restore=Y/N]Perform reliability calcs: Failure rates and number of interruptions.     Optional parameter:    If restore=y automatic restoration of unfaulted section is assumed. |
| Remove | {ElementName=} [KeepLoad=Y*/N] [EditString="..."] Remove (disable) all branches downline from the PDelement named by "ElementName" property. Circuit must have an Energymeter on this branch. If KeepLoad=Y (default) a new Load element is defined and kW, kvar set to present power flow solution for the first element eliminated. The EditString is applied to each new Load element defined.   If KeepLoad=N, all downline elements are disabled. Examples:     Remove Line.Lin3021  Remove Line.L22 Editstring="Daily=Dailycurve Duty=SolarShape  Remove Line.L333 KeepLoad=No |
| Rephase | Generates a script to change the phase designation of all lines downstream from a start in line. Useful for such things as moving a single-phase lateral from one phase to another and keep the phase designation consistent for reporting functions that need it to be (not required for simply solving).     StartLine=... PhaseDesignation="..."  EditString="..." ScriptFileName=... StopAtTransformers=Y/N/T/F    Enclose the PhaseDesignation in quotes since it contains periods (dots).  You may add and optional EditString to edit any other line properties.    Rephase StartLine=Line.L100  PhaseDesignation=".2"  EditString="phases=1" ScriptFile=Myphasechangefile.DSS  Stop=No |
| ReprocessBuses | Forces reprocessing of bus definitions whether there has been a change or not. Use for rebuilding meter zone lists when a line length changes, for example or some other event that would not normally trigger an update to the bus list. |
| Reset | {MOnitors | MEters | Faults | Controls | Eventlog | Keeplist |(no argument) } Resets all Monitors, Energymeters, etc. If no argument specified, resets all options listed. |
| Rotate | Usage: Rotate [angle=]nnn.  Rotate circuit plotting coordinates by specified angle (degrees). |
| Sample | Force all monitors and meters to take a sample for the most recent solution. Keep in mind that meters will perform integration. |
| Save | {Save [class=]{Meters | Circuit | Voltages | (classname)} [file=]filename [dir=]directory     Default class = Meters, which saves the present values in both monitors and energy meters in the active circuit.     "Save Circuit" saves the present enabled circuit elements to the specified subdirectory in standard DSS form with a Master.txt file and separate files for each class of data.     If Dir= not specified a unique name based on the circuit name is created automatically.     If Dir= is specified, any existing files are overwritten.     "Save Voltages" saves the present solution in a simple CSV format in a file called DSS_SavedVoltages. Used for VDIFF command.    Any class can be saved to a file.  If no filename specified, the classname is used. |
| Select | Selects an element and makes it the active element.  You can also specify the active terminal (default = 1).    Syntax:  Select [element=]elementname  [terminal=]terminalnumber     Example:  Select Line.Line1   ~ R1=.1  (continue editing)    Select Line.Line1 2   Voltages  (returns voltages at terminal 2 in Result) |
| SeqCurrents | Returns the sequence currents into all terminals of the active circuit element (see Select command) in Result string.  Returned as comma-separated magnitude only values.Order of returned values: 0, 1, 2  (for each terminal). |
| Seqpowers | Returns the sequence powers into all terminals of the active circuit element (see Select command) in Result string.  Returned as comma-separated kw, kvar pairs.Order of returned values: 0, 1, 2  (for each terminal). |
| Seqvoltages | Returns the sequence voltages at all terminals of the active circuit element (see Select command) in Result string.  Returned as comma-separated magnitude only values.Order of returned values: 0, 1, 2  (for each terminal). |
| Set | Used to set various DSS solution modes and options.  You may also set the options with the Solve command. See "Options" for help. |
| SetBusXY | Bus=...  X=...  Y=... Set the X, Y coordinates for a single bus. Prerequisite: Bus must exist as a result of a Solve, CalcVoltageBases, or MakeBusList command. |
| SetkVBase | Command to explicitly set the base voltage for a bus. Bus must be previously defined. Parameters in order are:  Bus = {bus name}  kVLL = (line-to-line base kV)  kVLN = (line-to-neutral base kV)    kV base is normally given in line-to-line kV (phase-phase). However, it may also be specified by line-to-neutral kV.  The following exampes are equivalent:    setkvbase Bus=B9654 kVLL=13.2  setkvbase B9654 13.2  setkvbase B9654 kvln=7.62 |
| SetLoadAndGenKV | Set load and generator object kv to agree with the bus they are connected to using the bus voltage base and connection type. |
| Show | Writes selected results to a text file and brings up the default text editor (see Set Editor=....) with the file for you to browse.    See separate help on Show command.     Default is "show voltages LN Seq". |
| Solve | Perform the solution of the present solution mode. You can set any option that you can set with the Set command (see Set). The Solve command is virtually synonymous with the Set command except that a solution is performed after the options are processed. |
| SolveAll | Solves all the circuits (Actors) loaded into memory by the user |
| Summary | Returns a power flow summary of the most recent solution in the global result string. |
| Tear_Circuit | Estimates the buses for tearing the system in many parts as CPUs - 1 are in the local computer, is used for tearing the interconnected circuit into a balanced (same number of nodes) collection of subsystems for the A-Diakoptics algorithm |
| TOP | [class=]{Loadshape | Tshape | Monitor  } [object=]{ALL (Loadshapes only) | objectname}. Send specified object to TOP.  Loadshapes and TShapes must be hourly fixed interval. |
| TotalPowers | Returns the total powers (complex) at ALL terminals of the active circuit element in the Result string. (See Select command.)Returned as comma-separated kW and kvar. |
| Totals | Totals all EnergyMeter objects in the circuit and reports register totals in the result string. |
| UpdateStorage | Update Storage elements based on present solution and time interval. |
| Userclasses | List of user-defined DSS Classes. Returns comma-separated list in Result variable. |
| Uuids | Read UUIDs (v4) for class names and other CIM objects. Tab or comma-delimited file with full object name (or key) and UUID. Side effect is to start a new UUID list for the Export CIM100 command; the UUID list is freed after the Export UUIDs command. |
| var | Define and view script variables.  Variable names begin with "@"    Usage:    var @varname1=values  @varname2=value2    ...  var @varname1  (shows the value of @varname1)  var            (displays all variabiles and values)    Example of using a variable:    FileEdit @LastFile |
| Variable | [name=] MyVariableName  [Index=] IndexofMyVariable     Returns the value of the specified state variable of the active circuit element, if a PCelement. Returns the value as a string in the Result window or the Text.Result interface if using the COM server.     You may specify the variable by name or by its index. You can determine the index using the VarNames command. If any part of the request is invalid, the Result is null. |
| Varnames | Returns variable names for active element if PC element. Otherwise, returns null. |
| VarValues | Returns variable values for active element if PC element. Otherwise, returns null. |
| Vdiff | Displays the difference between the present solution and the last on saved using the SAVE VOLTAGES command. |
| Visualize | [What=] one of {Currents* | Voltages | Powers} [element=]full_element_name  (class.name). Shows the selected quantity for selected element on a multiphase line drawing in phasor values. |
| Voltages | Returns the voltages for the ACTIVE BUS in the Result string. For setting the active Bus, use the Select command or the Set Bus= option. Returned as magnitude and angle quantities, comma separated, one set per conductor of the terminal. |
| Wait | Pauses the scripting thread until all the active actors are Ready to receive new commands (have finished all their tasks and are ready to receive new simulation orders). |
| YearlyCurves | [cases=](case1, case2, ...) [registers=](reg1, reg2, ...)  [meter=]{Totals* | SystemMeter | metername}Plots yearly curves for specified cases and registers.   Default: meter=Totals. Example:     yearlycurves cases=(basecase, pvgens) registers=9 |
| Ysc | Returns full Ysc matrix for the ACTIVE BUS in comma-separated complex number form G + jB. |
| Zsc | Returns full Zsc matrix for the ACTIVE BUS in comma-separated complex number form. |
| Zsc012 | Returns symmetrical component short circuit impedances Z0, Z1, and Z2 for the ACTIVE 3-PHASE BUS. Determined from Zsc matrix. |
| Zsc10 | Returns symmetrical component impedances, Z1, Z0 for the ACTIVE BUS in comma-separated R+jX form. |
| ZscRefresh | Refreshes Zsc matrix for the ACTIVE BUS. |

© 2024 Electric Power Research Institute (EPRI), Inc. All rights reserved. Electric Power Research Institute and EPRI are registered marks of the Electric Power Research Institute, Inc. in the U.S. and worldwide.

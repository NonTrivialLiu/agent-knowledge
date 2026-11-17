---
title: "MATPOWER AC Power Flow"
url: https://matpower.app/manual/matpower/ACPowerFlow.html
published: 
fetched: 2026-11-17
type: docs
topics: [tools-execution, matpower, powerflow, constraints]
summary: "AC 潮流默认不强制设备限值，无功限值外循环改变母线类型；区分收敛与运行可行性。"
---

# MATPOWER AC Power Flow

In Matpower, by convention, a single generator bus is typically chosen as a reference bus to serve the roles of both a voltage angle reference and a real power slack. The voltage angle at the reference bus has a known value, but the real power generation at the slack bus is taken as unknown to avoid overspecifying the problem. The remaining generator buses are typically classiﬁed as PV buses, with the values of voltage magnitude and generator real power injection given. These are speciﬁed in the VG (6) and PG (3) columns of the gen matrix, respectively. Since the loads and are also given, all non-generator buses are classiﬁed as PQ buses, with real and reactive injections fully speciﬁed, taken from the PD (3) and QD (4) columns of the bus matrix. Let , and denote the sets of bus indices of the reference bus, PV buses and PQ buses, respectively. The bus type classiﬁcation is speciﬁed in the Matpower case ﬁle in the BUS\_TYPE column (2) of the bus matrix. Any isolated buses must be identiﬁed as such in this column as well.

In the traditional formulation of the AC power ﬂow problem, the power balance
equation in ([3.17](NetworkEquations.html#eq:acpf)) is split into its real and reactive components, expressed as functions of
the voltage angles  and magnitudes  and generator injections  and , where
the load injections are assumed constant and given:

For the AC power ﬂow problem, the function  from ([4.1](PowerFlow.html#eq:gx0)) is formed by taking the
left-hand side of the real power balance equations ([4.2](#eq:acpf_p)) for all non-slack buses
and the reactive power balance equations ([4.3](#eq:acpf_q)) for all PQ buses and plugging in
the reference angle, the loads and the known generator injections and voltage
magnitudes:

|      | (4.4) | 

The vector consists of the remaining unknown voltage quantities, namely the voltage angles at all non-reference buses and the voltage magnitudes at PQ buses:

|      | (4.5) | 

This yields a system of nonlinear equations with equations and unknowns, where and are the number of PV and PQ buses, respectively. After solving for , the remaining real power balance equation can be used to compute the generator real power injection at the slack bus. Similarly, the remaining reactive power balance equations yield the generator reactive power injections.

Matpower includes four diﬀerent algorithms for solving the general AC power ﬂow
problem.<sup>26</sup> 
[The default solver is based on a standard Newton’s method \[][10](tocbibnameprwmkbothtocbibname.html#Xtinney1967)\] using a polar
form and a full Jacobian updated at each iteration. Each Newton step involves
computing the mismatch , forming the Jacobian based on the sensitivities of
these mismatches to changes in  and solving for an updated value of  by
factorizing this Jacobian. This method is described in detail in many textbooks. As of
version 7, Matpower also includes variants of the Newton method using nodal
current balance equations and/or cartesian representations for voltage as described
in \[[11](tocbibnameprwmkbothtocbibname.html#Xsereeter2019)\].

Also included are solvers based on variations of the fast-decoupled method \[[12](tocbibnameprwmkbothtocbibname.html#Xstott1974)\],
speciﬁcally, the XB and BX methods described in \[[13](tocbibnameprwmkbothtocbibname.html#Xamerongen1989)\]. These solvers greatly reduce the
amount of computation per iteration, by updating the voltage magnitudes and angles
separately based on constant approximate Jacobians which are factored only once at the
beginning of the solution process. These per-iteration savings, however, come at the cost of
more iterations.

The fourth algorithm is the standard Gauss-Seidel method from Glimm and
Stagg \[[14](tocbibnameprwmkbothtocbibname.html#Xglimm1957)\]. It has numerous disadvantages relative to the Newton method and is included
primarily for academic interest.

By default, the AC power ﬂow solvers simply solve the problem described above,
ignoring any generator limits, branch ﬂow limits, voltage magnitude limits, etc. However,
there is an option (pf.enforce\_q\_lims) that allows for the generator reactive
power limits to be respected at the expense of the voltage setpoint. This is done
                                                                                  
                                                                                  
in a rather brute force fashion by adding an outer loop around the AC power
ﬂow solution. If any generator has a violated reactive power limit, its reactive
injection is ﬁxed at the limit, the corresponding bus is converted to a PQ bus
and the power ﬂow is solved again. This procedure is repeated until there are
no more violations. Note that this option is based solely on the QMAX and QMIN
parameters for the generator, from columns 4 and 5 of the gen matrix, and does
not take into account the trapezoidal generator capability curves described in
Section [6.4.3](StandardExtensions.html#sec:cap_curve) and specifed in columns PC1–QC2MAX (11–16). Note also that this
option aﬀects generators even if the bus they are attached to is already of type
PQ.

In all, there are 4 diﬀerent formulations implemented for the Newton power ﬂow,
described brieﬂy below, with the details found in reference \[[11](tocbibnameprwmkbothtocbibname.html#Xsereeter2019)\].

Another variation of the standard AC power ﬂow problem represents the bus voltages in
cartesian, rather than polar, coordinates. That is, instead of  and , the vector  of
unknowns includes the real and imaginary parts of the complex voltage, denoted
respectively by  and , where . The active and reactive power
balance equations from ([4.2](#eq:acpf_p))–([4.3](#eq:acpf_q)) are then expressed as functions of  and
.

The power ﬂow problem of ([4.4](#eq:g_acpf)) becomes

|                                                                                                                                                                            | (4.8) | 

where

|      | (4.9) | 

For PV buses, since the voltage magnitude is constant, can be expressed as a function of , allowing to be eliminated for PV buses by modifying the Jacobian terms corresponding to and . This results once again in a system of nonlinear equations with equations and unknowns.

In Matpower setting the pf.v\_cartesian option to 1 (0 by
default) selects the cartesian representation for voltages when running a
Newton-Raphson AC power ﬂow, that is, when the pf.alg option is set to
'NR'.<sup>27</sup> 

Another variation of the standard AC power ﬂow problem uses current balance equations
in place of the power balance equations in ([4.4](#eq:g_acpf)) and ([4.8](#eq:g_acpf_SC)). If we let  and  represent
the real and imaginary parts, respectively, of the current, we can express the current
balance functions for the polar form as

and for the cartesian form as

where , and is a diagonal matrix whose -th diagonal entry is , that is or .

In order to handle PV buses, is expanded to include the full set of mismatch equations for all PV and PQ buses, and the reactive power injections at PV buses are added to as independent variables, resulting in a system of nonlinear equations with equations and unknowns.

In Matpower setting the pf.current\_balance option to 1 (0 by default)
selects the current balance version when running a Newton-Raphson AC
power ﬂow, that is, when the pf.alg option is set to 'NR'. This option can be
used in conjunction with either the polar or cartesian representation of bus
voltages.<sup>28</sup>

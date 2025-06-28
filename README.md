# Plasticity induced crack closure under plane stress assumption

Author :  Solène Grappein

# Table of Contents

- [Plasticity induced crack closure under plane stress assumption](#plasticity-induced-crack-closure-under-plane-stress-assumption)
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Numerical model](#numerical-model)
  - [Geometry and properties of the specimen](#geometry-and-properties-of-the-specimen)
  - [Cyclic loading](#cyclic-loading)
  - [Mesh refinement](#mesh-refinement)
  - [Boundary conditions and node release method](#boundary-conditions-and-node-release-method)
  - [Contact between the two faces of the crack](#contact-between-the-two-faces-of-the-crack)
- [How to use the different files](#how-to-use-the-different-files)

# Introduction

The objective of this work is to study the phenomenon of plasticity induced crack closure. In order to do this, the first step is to model an edge crack under cyclic loading, under plain stress assumption. We will compare the results of crack opening with a theoretical article from Vilder and al. In this work, we are trying to replicate the model done by Tomáš Oplt et al.

In the file picc-v2.py you will find a script written from A to Z and ready to run on Abaqus. It will create the model and the job, ready to submit. The model created is explained here after. The file post-process.py can process the data of force and displacement, in order to determine the crack opening load with the compliance method. The file automate.py is used to automatically do several calculations.

# Numerical model

## Geometry and properties of the specimen

The specimen we study is an edge-cracked plate. Due to the geometric and loading symmetry, we will only model the upper half of the specimen.

Near the initial crack tip, we are doing a partition to refine the mesh here. That is why two rectangles are created : the small one around the crack tip and the larger one is a transition rectangle. The dimensions of the small rectangle are very important and depend on the plasticity zone size.

The material is an elastic – perfectly plastic material with the following properties : \
E = 210 000 MPa \
$\sigma_y$ = 250 MPa

However, due to convergence issues, a slight hardening is introduced in the numerical implementation, allowing the material behavior to approximate perfect plasticity while maintaining numerical stability.


## Cyclic loading

The cyclic loading applied in this model ranges from 0 MPa to 25 MPa, corresponding to a stress ratio of $\frac{\sigma_{max}}{\sigma_y} = 0.1$ which is used in the literature. A cycle is defined by many substeps. Indeed, it allows a smoother calculation and avoir convergence issues. In my case, and following some advices in the literature, the substeps I use are : \

- First phase - the loading : 10 steps 
- Second phase - the debond : 1 step
- Last phase - the unloading : 30 steps

The crack must grow enough so that the phenomenom of plasticity induced crack closure is visible. For this reason, we apply 20 loading cycles.


## Mesh refinement


The elements using are quadrilateral. Concerning the size of the mesh, the literature shows the importance of having a fine mesh around the crack tip. The size of the mesh depends on the size of the plasticity zone. 

That is the reason why we define a zone where the mesh is very fine near the crack tip. The element length is $L_e$ $= 0.1$ $r_p$ with $r_p$ the size of the zone of plasticity. This zone can be calculated with the formula : 

$r_p = \frac{1}{2 \alpha \pi}(\frac{K_{max}}{\sigma_0})^2$

In our case, we conclude that : $r_p = 0.0074 a$. So, the element length near the crack tip must be 7.4 microns. This fine zone is $4 r_p$ width and 1 $r_p$ high. 


## Boundary conditions and node release method

As we only model the upper part of the specimen, the bottom part of our structure must be fixed, due to symmetry conditions.

To model the crack growth, we are using the node release method. At the end of each cycle, one node is released so the crack opens a little more. 


## Contact between the two faces of the crack

As we are modelling only the upper part of the specimen and so only the upper face of the crack, we must model the second one to analyse the closure of it. In order to do that, we model the second face of the crack with a line of master elements. The upper face will be the slave elements and so, a contact can be established with a penalty method. The penalty factor is taken to 30.


# How to use the different files

To run a numerical model of edge-crack specimen under cyclic loading, you have to run the script `picc-ready` in Abaqus. It will create the model and the job ready to submit. Some parameters can be changed in the script : for example the values of the load, the R-ratio, the stress ratio, the number of cycles or of substeps. 

Several calculations can be started with the file `automate`. You have to define your parameters in it, for now it is the values of the load depending on the r-ratio. Then, use a prompt command to run it : on Windows, use the command `abaqus automate.py` to begin the calculations. It will run the file `picc-v2` with all your parameters.

After the calculation you can save the information you are interested in directly in Abaqus. If you have force-displacement data, you can use the file `post-process`. It will plot a lot of figures and give many information. It will repere the different cycles, calculate the stiffness by deriving the force-displacement curve and use linear regression in order to find the crack opening and crack closure load ratios.

You have to complete some information for the file to work. 

- Line 11, the name of your file : `excel_file = "force-displacement-20-cycles-0-3_0-1.xlsx"`
- Line 98, the number of the cycle you want to study : `cycle = 20`
- Line 99, the minimal force between each cycle : `force_min = 1200`
- Line 209, 268, 412 and 471 you can put the parameters for your linear regressions : 
```python
max_slopes1 = 1500000
min_slopes1 = 142000

max_disps1 = 0.021
min_disps1 = 0.012
```




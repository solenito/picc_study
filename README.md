# Plasticity induced crack closure under plane stress assumption

## Introduction

The objective of this work is to study the phenomenon of plasticity induced crack closure. In order to do this, the first step is to model an edge crack under cyclic loading, under plain stress assumption. We will compare the results of crack opening with a theoretical article from Vilder and al. In this work, we are trying to replicate the model done by Tomáš Oplt et al.

In the file `picc-v2.py` you will find a script written from A to Z and ready to run on Abaqus. It will create the model and the job, ready to submit. The model created is explained here after.
The file 'post-process.py' can process the data of force and displacement, in order to determine the crack opening load with the compliance method.
The file 'automate.py' is used to automatically do several calculations.

## Numerical model

The specimen we study is an edge-cracked plate. Due to the geometric and loading symmetry, we will only model the upper half of the specimen.

Near the initial crack tip, we are doing a partition to refine the mesh here. That is why two rectangles are created : the small one around the crack tip and the larger one is a transition rectangle. The dimensions of the small rectangle are very important and depend on the plasticity zone size.

The material is an elastic – perfectly plastic material with the following properties : 

- E = 210 000 MPa 
- $\sigma_y$ = 250 MPa

However, due to convergence issues, a slight hardening is introduced in the numerical implementation, allowing the material behavior to approximate perfect plasticity while maintaining numerical stability.


## Cyclic loading

The cyclic loading applied in this model ranges from 0 MPa to 25 MPa, corresponding to a stress ratio of $\frac{\sigma_{max}}{\sigma_y} = 0.1$ which is used in the literature. A cycle is defined by many substeps. Indeed, it allows a smoother calculation and avoir convergence issues. In my case, and following some advices in the literature, the substeps I use are : 

- First phase - the loading : 10 steps 
- Second phase - the debond : 1 step
- Last phase - the unloading : 30 steps

The crack must grow enough so that the phenomenon of plasticity induced crack closure is visible. For this reason, we apply 20 loading cycles.


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




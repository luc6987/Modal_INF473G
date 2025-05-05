# Modal_INF473G

First, we extract the data from the soup to .json with the following headers with first_extraction.py .

  {
    "paper_id": "hep-th/9211088",
    "from": "gervais@physique.ens.fr (GERVAIS Jean-Loup)",
    "submitted": "Thu, 19 Nov 92 15:16:52 +0100 (13kb)",
    "title": "Gauge Conditions for the Constrained-WZNW--Toda Reductions",
    "authors": "Jean-Loup Gervais, Lochlainn O'Raifeartaigh, Alexander V. Razumov, Mikhail V. Saveliev",
    "comments": "12 pages, no figures",
    "report_no": "DIAS--92/27, IHEP 92-155, LPTENS--92/40, NI92008",
    "journal_ref": "Phys.Lett. B301 (1993) 41-48",
    "subject_class": null,
    "proxy": null,
    "abstract": "There is a constrained-WZNW--Toda theory for any simple Lie algebra equipped with an integral gradation. It is explained how the different approaches to these dynamical systems are related by gauge transformations. Combining Gauss decompositions in relevent gauges, we unify formulae already derived, and explictly determine the holomorphic expansion of the conformally reduced WZNW solutions - whose restriction gives the solutions of the Toda equations. The same takes place also for semi-integral gradations. Most of our conclusions are also applicable to the affine Toda theories.",
    "year": 1992
  },

To clean the names, there are two parts:

First we read the line and break it in to names to form a namelist with nom.py. Then, we clean the namelist with standarniee_name.py .

Then we use the cleaned namelist to rewrite the output.json.


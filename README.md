# UniverSQL

In this Repo we provide an NLIDB API for use with models from the [Spider](https://yale-lily.github.io/spider) and [SparC](https://yale-lily.github.io/sparc) challenges.

UniverSQL is a small python application that can be used as translation server.
The API allows unified access to most important functions (select a database, select a translator, do the actual translation) and to some convenience and debugging functions like logging.
It can be used for single translations but also for (context preserving) multi-turn interactions like proposed in the SparC challenge.

The core of UniverSQL is a wrapper implementation to allow running arbitrary queries on pre-trained models.
We provide two sample implementations of this wrapper together with setup scripts for two systems from the Spider leaderboard (see below).
Contributions to support more approaches are more than welcome.

We further describe this API and its background in a paper currently under submission which we will link here soon.

[Setup](SETUP.md) - [Extension: Support more approaches](Extension.md) - [Development: Contribute to this application](Development.md)

## Supported approaches

Currently, the following models from the Spider and SparC leaderboards are supported:

| Approach name | Implemented by           | Links                                                   |
| ------------- | ------------------------ | ------------------------------------------------------- |
| EditSQL       | Hättasch, Geisler et al. | [Code](https://github.com/DataManagementLab/univerSQL/tree/master/nlidbTranslator/api/adapters/editsql) - [Original Code](https://github.com/ryanzhumich/editsql) |
| IRNet       | Hättasch, Geisler et al. | [Code](https://github.com/DataManagementLab/univerSQL/tree/master/nlidbTranslator/api/adapters/IRNet) - [Original Code](https://github.com/microsoft/IRNet) |

You implemented a wrapper and installation script for another approach? Feel free to either contribute by opening a pull request or contacting us to have the link to your codebase intregrated here.


## Cite

If you are using our API for our research, please cite it as follows:

```
Benjamin Hättasch, Nadja Geisler, and Carsten Binnig: Under submission, coming soon
```

You probably also want to cite Spider and SparC in that case:

```
@inproceedings{Yu&al.18c,
  year =         2018,
  title =        {Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task},
  booktitle =    {EMNLP},
  author =       {Tao Yu and Rui Zhang and Kai Yang and Michihiro Yasunaga and Dongxu Wang and Zifan Li and James Ma and Irene Li and Qingning Yao and Shanelle Roman and Zilin Zhang and Dragomir Radev }
}

@InProceedings{Yu&al.19,
  title     = {SParC: Cross-Domain Semantic Parsing in Context},
  author    = {Tao Yu and Rui Zhang and Michihiro Yasunaga and Yi Chern Tan and Xi Victoria Lin and Suyi Li and Heyang Er, Irene Li and Bo Pang and Tao Chen and Emily Ji and Shreya Dixit and David Proctor and Sungrok Shim and Jonathan Kraft, Vincent Zhang and Caiming Xiong and Richard Socher and Dragomir Radev},
  booktitle = {Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics},
  year      = {2019},
  address   = {Florence, Italy},
  publisher = {Association for Computational Linguistics}
}
```

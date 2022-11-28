<style>
.figure{
    width: 80%;
    margin: 0 auto;
    padding: 0px;
}
</style>

#CI / CD Pipeline

The CI/CD  pipeline consists of three stages: *Test*, *Coverage* and *Deploy*.
In the Test stage unit and integrations tests and a lint check are executed.
Due to a high test coverage we make sure that all PFDL programs will be parsed correctly and the scheduler works as he should.
With the Linter we check for coding guideline violations and assure that the code satisfies them to a certain degree.
If all tests are passed the coverge stage measures the code coverage of the unit and integration tests and creates an detailed report about it.
Last but not least the deploy stage starts where the documentation and the code is build.

This pipeline starts on every push to the main repository. The different stages and jobs of the pipeline are depicted in the figure below.

<div class="figure">
<img src="../../img/pipeline.png#only-light" alt="CI/CD pipeline"/>
<img src="../../img/pipeline_dark.png#only-dark" alt="CI/CD pipeline"/>
<br><br>
<b>Fig.1:</b> The CI/CD pipeline which is executed after every push to the main repository. It consists of the stages test and deploy.

<br><br>
</div>
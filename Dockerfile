FROM condaforge/mambaforge:22.11.1-4

# Use conda instead of mamba
COPY environment.yml .
RUN conda env create -f environment.yml && conda clean -afy

# Download required MFA models
RUN conda run -n mfa_env mfa model download acoustic english_mfa && \
    conda run -n mfa_env mfa model download dictionary english_mfa


ENV PATH /opt/conda/envs/mfa_env/bin:$PATH

WORKDIR /app
COPY app.py requirements.txt ./

RUN conda run -n mfa_env pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

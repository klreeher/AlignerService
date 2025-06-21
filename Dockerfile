FROM condaforge/mambaforge:22.11.1-4

# Install MFA and Flask
COPY environment.yml .
RUN mamba env create -f environment.yml && \
    conda clean -afy
# Activate in container
RUN echo "source activate mfa_env" > ~/.bashrc
ENV PATH /opt/conda/envs/mfa_env/bin:$PATH

WORKDIR /app
COPY app.py requirements.txt ./

RUN conda run -n mfa_env pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

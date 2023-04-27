# Define function directory
ARG FUNCTION_DIR="/var/task"

FROM python:3.8 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY . ${FUNCTION_DIR}

# Install the runtime interface client
RUN pip install \
  --target ${FUNCTION_DIR} \
  awslambdaric

RUN pip install \
  --target ${FUNCTION_DIR} \
  -r ${FUNCTION_DIR}/requirements.txt

# Multi-stage build: grab a fresh copy of the base image
FROM public.ecr.aws/lambda/python:3.8

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

#ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.function_main" ]
![MLOps Zoomcamp](../images/banner-2025.jpg)
---

## 📚 MLOps Zoomcamp Capstone Project Reviews

During the program, we completed capstone projects that were peer-reviewed, providing valuable insights into our work. This document summarizes comprehensive feedback on three capstone projects from the DataTalksClub MLOps Zoomcamp. Each review highlights the projects' strengths and areas for improvement, and lessons learned. These insights aim to guide future machine learning projects and foster continuous improvement.

---

### [🔍 Project 01 Review: Stocks Forecasting](https://github.com/OnurKerimoglu/stocks_forecasting_live)

✅ What Went Well:    
	•	Clear Documentation: The project is well-documented, and the snapshot showcasing the infrastructure adds excellent clarity.   
	•	User-Centric Visualization: The addition of a Streamlit (or other visual) app was a great decision — this significantly enhances accessibility for non-technical viewers.    
	•	Code Quality: Overall, the project structure is solid, and there’s great potential here. GREAT WORK DONE!   


🛠️ Suggestions for Improvement:   
	•	Problem description: Providing clearer on what is the goal of the project is very important as it helps understand what problem is it that you are trying to solve.   
	•	Thoughtful Tooling: There are other (simpler) methods like mlcroissant and curl for downloading data from Kaggle. This might be helpful.    
	•	Branching Strategy Clarity: having both dev and prod branches seems to be considered a best practice, more explanation about your rationale (e.g., CI/CD pipeline use, release management) would have been helpful. Also, consider making prod the default branch if that’s the one meant for general users.    
	•	Project Planning: Instead of only giving build instructions, a planning document outlining the step-by-step development flow would have been very helpful. A high-level architecture or roadmap diagram is already available.   
	•	End-to-End Notebook: A single notebook that ties the project together from data to deployment would be invaluable — especially for demonstration, reproducibility, and onboarding. It can even mae your work easier.    
	•	Docstrings and Comments: Adding docstrings to your functions would improve readability and maintainability, especially in collaborative environments.   

🧠 Final Thought:    

There’s a lot of solid work here, but some of it isn’t fully visible due to the lack of surfacing key elements (planning docs, central notebooks, etc.). Highlighting your workflow and decisions more clearly would make the project even more impactful.


---


### [🔍 Project 02 Review: Stock Prediction](https://github.com/hsviscarra/StockPrediction)

⚠️ Submission Integrity & Structure      
	•	Commit Hash Mismatch: I had difficulty locating the correct version to review, as the commit hash provided pointed to a forked repository rather than the main one. In the future, please double-check the reference you submit to avoid confusion.    
	•	Project Structure Issues: The structure in the submitted files seems a bit off — it’s unclear if this was intentional. Make sure to preview the repository layout before submitting, to ensure everything appears as expected.   

🧩 Documentation & Clarity    
	•	Undefined Acronyms: The problem description includes acronyms that aren’t explained. It reads as if it’s written for someone already deeply familiar with the domain. Try to spell out and explain acronyms at least once, especially in public-facing documents like the README.
	•	README Improvements Needed:    
	•	The README lacks a clear step-by-step plan or pipeline describing how the project was built.   
	•	Execution instructions are vague, which could make it harder for others to reproduce your work.   
	•	That said, I appreciate the help option in the Makefile — that’s a helpful touch for usability!   


---

### [🔍 Project 03 Review: Brain Eye Detector](https://github.com/Shayanix/MLops-Brain-Eye-Detector)


🌟 What Stood Out   
	•	Novel and Fascinating Idea: This is the first time I’ve encountered a project that attempts to determine whether eyes are open or closed using brain wave data. It’s not only interesting but also opens the door to fascinating applications in neuroscience and human-computer interaction.   
	•	Clear Structure and Presentation: The repository is well-organized, and the problem statement is concisely described, making it easy to follow the general intent of the project.   

📉 Areas for Improvement   
	•	Dataset Description & Target Variable:   
	    •	It would be helpful to explain the dataset more thoroughly.   
	    •	For example, clarify what the target variable represents: is 0 for closed or open eyes?   
	•	Bash Code Formatting: There were some formatting issues in your bash code snippets. Make sure to improve readbility.   
	•	Model Registry Misuse:   
	    •	The model was logged but not registered properly in the MLflow model registry.   
	    •	This may explain the issues with CI/CD failures — there’s a difference between logging and registering a model. You need to explicitly register it if you want to refer to it across environments.    

💡 Final Note    

There’s so much potential in this project! The foundation is promising, but there’s clearly more that could be done — from expanding documentation, improving code integration, to leveraging model tracking and deployment more effectively. I truly hope you continue to build on it.   


----

For more fun: review my [capstone project](https://github.com/maxim-eyengue/Machine-RUL-Predictor).   


---

# References and Attribution

## Scientific references

1. **SSIM**  
   Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004).  
   *Image quality assessment: From error visibility to structural similarity*.  
   IEEE Transactions on Image Processing, 13(4), 600–612.  
   DOI: https://doi.org/10.1109/TIP.2003.819861  
   Used here through `skimage.metrics.structural_similarity`.

2. **OpenCV perspective geometry**  
   The implementation uses OpenCV's `getPerspectiveTransform` and `warpPerspective` for a projective transform/homography. These are standard computer-vision operations; the local project does not claim a new homography algorithm.
   - OpenCV documentation: https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html

3. **Chess rules and legal move generation**  
   The project delegates chess rules and legal move generation to `python-chess`.
   - Documentation: https://python-chess.readthedocs.io/
   - Repository: https://github.com/niklasf/python-chess

4. **Stockfish**  
   Stockfish is an external UCI chess engine. Its search, NNUE evaluation and implementation are not original algorithms of this project.
   - Website: https://stockfishchess.org/
   - Repository: https://github.com/official-stockfish/Stockfish
   - Project-local citation and license files: `latest/stockfish/CITATION.cff` and `latest/stockfish/Copying.txt`

## Local algorithms and design contributions

The following parts are project-specific engineering logic, not claims of new scientific algorithms:

- Reusing calibrated board corners instead of running detection on every frame.
- Mapping 8×8 image cells to algebraic squares.
- Selecting changed squares from SSIM scores.
- Handling special castling patterns.
- Constraining observed changes to legal moves and comparing symmetric differences.
- Translating UCI moves into calibrated pick/place/throw sequences.
- Verifying the robot move with a subsequent visual observation.

## External services and hardware

- IP Camera application on a phone, providing an HTTP still-image endpoint.
- Arduino Uno and servo motors.
- Roboflow Inference/model endpoint may be used by the optional corner detector. The model identifier currently referenced by the code is `chessboard-detection-yqcnu/3`; its accuracy and availability must be verified independently.

## Citation suggestion

```bibtex
@software{chess_robot_prototype,
  title  = {Vision-Guided Robotic Chessboard},
  author = {Project contributors},
  year   = {2026},
  note   = {Prototype integrating IP camera vision, python-chess, Stockfish, Arduino, and a 6-DOF robotic arm}
}
```


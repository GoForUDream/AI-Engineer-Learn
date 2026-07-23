import { z } from "zod";


const UploadedFileDtoSchema = z.object({
  id: z.uuid(),
  owner_id: z.string().min(1),
  original_name: z.string().min(1),
  content_type: z.string().min(1),
  size_bytes: z.number().int().positive(),
  uploaded_at: z.string().datetime({
    offset: true,
  }),
});


export type UploadedFileDto = z.infer<
  typeof UploadedFileDtoSchema
>;


export interface UploadedFile {
  id: string;
  ownerId: string;
  originalName: string;
  contentType: string;
  sizeBytes: number;
  uploadedAt: Date;
}


export function parseUploadedFile(
  value: unknown,
): UploadedFile {
  const dto = UploadedFileDtoSchema.parse(value);

  return {
    id: dto.id,
    ownerId: dto.owner_id,
    originalName: dto.original_name,
    contentType: dto.content_type,
    sizeBytes: dto.size_bytes,
    uploadedAt: new Date(dto.uploaded_at),
  };
}


export function parseUploadedFiles(
  value: unknown,
): UploadedFile[] {
  return z
    .array(UploadedFileDtoSchema)
    .parse(value)
    .map((dto) => ({
      id: dto.id,
      ownerId: dto.owner_id,
      originalName: dto.original_name,
      contentType: dto.content_type,
      sizeBytes: dto.size_bytes,
      uploadedAt: new Date(dto.uploaded_at),
    }));
}